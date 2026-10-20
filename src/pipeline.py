"""
RahiScan - Clean -> Explore -> Model -> Evaluate pipeline (on MOCK data)
=======================================================================

Reads data/raw/*, applies the cleaning rules described in the proposal,
engineers the Pace Index (Pi) and Fare Fairness Ratio (Phi), trains the two
proposed models and writes everything the report needs to data/processed/.

Run:  python src/pipeline.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import confusion_matrix, f1_score, mean_absolute_error, precision_score, recall_score

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

OCR_MIN, FACE_MIN = 0.85, 0.70
WALK_KMH, TAIL_MIN_S, ACCEL_WALK = 6.0, 60, 1.0
SLOW_T, FAST_T, OVER_T = 0.75, 1.15, 1.25

trips = pd.read_csv(RAW / "trips_raw.csv", parse_dates=["start_ts", "end_ts"])
scans = pd.read_csv(RAW / "scans.csv")
bench = pd.read_csv(RAW / "fare_benchmarks.csv")
reg = pd.read_csv(RAW / "drivers_registry.csv")
pings = pd.read_csv(RAW / "gps_pings.csv.gz", parse_dates=["ts"])

funnel = [("Raw ride submissions", len(trips))]

# ---------------------------------------------------------------- CLEAN 1: duplicates
trips = trips.sort_values(["user_id", "corridor", "start_ts"])
gap = trips.groupby(["user_id", "corridor"])["start_ts"].diff().dt.total_seconds()
trips = trips[~(gap.notna() & (gap < 10))].copy()
funnel.append(("Duplicate uploads removed", len(trips)))

# ---------------------------------------------------------------- CLEAN 2: fare validity
trips = trips.merge(bench, on="trip_id")
trips = trips[trips["quoted_fare_pkr"].notna()]
ratio = trips["quoted_fare_pkr"] / trips["benchmark_fare_pkr"]
trips = trips[(ratio > 0.4) & (ratio < 4.0)].copy()
funnel.append(("Missing / typo fares removed", len(trips)))

# ---------------------------------------------------------------- CLEAN 3: identity resolution
plate_map = reg.groupby("plate")["driver_id"].apply(list).to_dict()
face_map = dict(zip(reg["face_id"], reg["driver_id"]))
trips = trips.merge(scans[["trip_id", "ocr_plate_text", "ocr_confidence", "face_match_id", "face_similarity", "low_light"]], on="trip_id")


def plate_only(r):
    c = plate_map.get(r.ocr_plate_text)
    return c[0] if c else None


def fused(r):
    face_ok = r.face_similarity >= FACE_MIN
    cands = plate_map.get(r.ocr_plate_text) if r.ocr_confidence >= OCR_MIN else None
    if cands:
        if len(cands) == 1:
            return cands[0]
        if face_ok and face_map[r.face_match_id] in cands:  # shared rickshaw: face decides
            return face_map[r.face_match_id]
        return None
    return face_map[r.face_match_id] if face_ok else None


trips["id_plate_only"] = trips.apply(plate_only, axis=1)
trips["id_fused"] = trips.apply(fused, axis=1)
id_metrics = {}
for col in ["id_plate_only", "id_fused"]:
    m = trips[col].notna()
    id_metrics[col] = dict(
        coverage=round(float(m.mean()), 4),
        precision=round(float((trips.loc[m, col] == trips.loc[m, "true_driver_id"]).mean()), 4),
    )
trips = trips[trips["id_fused"].notna()].copy()
trips["driver_id"] = trips["id_fused"]
funnel.append(("Unverifiable identities removed", len(trips)))

# ---------------------------------------------------------------- CLEAN 4: GPS walking tails + dropouts


def hav(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    h = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(h))


rows = []
pg = pings[pings["trip_id"].isin(trips["trip_id"])].groupby("trip_id")
for tid, g in pg:
    g = g.sort_values("seq")
    lat = g["lat"].rolling(3, center=True, min_periods=1).mean().to_numpy()
    lon = g["lon"].rolling(3, center=True, min_periods=1).mean().to_numpy()
    t = (g["ts"] - g["ts"].iloc[0]).dt.total_seconds().to_numpy()
    seg = np.concatenate([[0], hav(lat[:-1], lon[:-1], lat[1:], lon[1:])])
    dt = np.concatenate([[5], np.diff(t)])
    spd = pd.Series(seg / np.maximum(dt, 1) * 3600).rolling(6, center=True, min_periods=1).median().to_numpy()
    acc = g["accel_var"].rolling(6, center=True, min_periods=1).median().to_numpy()
    # walk back from the end while the user moves at walking pace with high step variance
    k = len(g) - 1
    while k > 0 and spd[k] < WALK_KMH + 2 and acc[k] > ACCEL_WALK:
        k -= 1
    tail_s = t[-1] - t[k]
    cut = k + 1 if tail_s >= TAIL_MIN_S else len(g)
    dur_raw, dist_raw = t[-1], seg.sum()
    dur, dist = t[cut - 1], seg[:cut].sum()
    coverage = (cut) / (t[cut - 1] / 5 + 1)
    rows.append(dict(trip_id=tid, raw_duration_min=dur_raw / 60, raw_distance_km=dist_raw,
                     duration_min=dur / 60, distance_km=dist, tail_trimmed_s=t[-1] - t[cut - 1],
                     gps_coverage=min(coverage, 1.0)))
gps = pd.DataFrame(rows)
trips = trips.merge(gps, on="trip_id")
tail_true = trips["true_tail_s"] > 0
tail_pred = trips["tail_trimmed_s"] > 0
tail_metrics = dict(precision=round(float(precision_score(tail_true, tail_pred)), 4),
                    recall=round(float(recall_score(tail_true, tail_pred)), 4),
                    n_tails=int(tail_true.sum()))
trips = trips[trips["gps_coverage"] >= 0.75].copy()
funnel.append(("Low GPS coverage removed", len(trips)))
funnel.append(("Walking tails trimmed (kept)", len(trips)))

# ---------------------------------------------------------------- EXPLORE / FEATURES
trips["hour"] = trips["start_ts"].dt.hour
trips["hour_bucket"] = (trips["hour"] // 2) * 2
trips["weekend"] = (trips["weekday"] >= 5).astype(int)
trips["week"] = ((trips["start_ts"] - pd.Timestamp("2026-11-02")).dt.days // 7 + 1).clip(1, 4)
trips["v_obs_raw"] = trips["raw_distance_km"] / (trips["raw_duration_min"] / 60)
trips["v_obs"] = trips["distance_km"] / (trips["duration_min"] / 60)
# crowd-sourced ambient baseline: median speed of ALL drivers on that corridor, hour bucket, day type
trips["v_base"] = trips.groupby(["corridor", "hour_bucket", "weekend"])["v_obs"].transform("median")
trips["pace_index"] = trips["v_obs"] / trips["v_base"]
trips["pace_label"] = np.select([trips["pace_index"] < SLOW_T, trips["pace_index"] > FAST_T], ["Slow", "Fast"], "Normal")

# ---------------------------------------------------------------- MODEL A: fair-fare regressor
trips["corridor_code"] = trips["corridor"].str[:2].str[1].astype(int)
feat_f = ["distance_km", "v_base", "hour", "weekend", "corridor_code"]
tr, te = trips[trips["week"] <= 3], trips[trips["week"] == 4]
gbr = GradientBoostingRegressor(n_estimators=300, max_depth=3, learning_rate=0.05, random_state=7)
gbr.fit(tr[feat_f], tr["benchmark_fare_pkr"])
lin = LinearRegression().fit(tr[["distance_km"]], tr["benchmark_fare_pkr"])
fare_pred_te = gbr.predict(te[feat_f])
fare_metrics = dict(
    gbr_mae=round(float(mean_absolute_error(te["benchmark_fare_pkr"], fare_pred_te)), 2),
    linear_distance_only_mae=round(float(mean_absolute_error(te["benchmark_fare_pkr"], lin.predict(te[["distance_km"]]))), 2),
    flat_rate_mae=round(float(mean_absolute_error(te["benchmark_fare_pkr"], np.full(len(te), tr["benchmark_fare_pkr"].median()))), 2),
    feature_importance=dict(zip(feat_f, np.round(gbr.feature_importances_, 4).tolist())),
)
trips["fair_fare_pred"] = gbr.predict(trips[feat_f])
trips["fare_ratio"] = trips["quoted_fare_pkr"] / trips["fair_fare_pred"]

# ---------------------------------------------------------------- MODEL B: pace classifier
trips = trips.merge(reg[["driver_id", "true_pace_class", "true_fare_class"]], on="driver_id", how="left")
feat_p = ["pace_index", "v_obs", "v_base", "distance_km", "hour", "weekend"]
feat_raw = ["v_obs", "distance_km"]
tr, te = trips[trips["week"] <= 3], trips[trips["week"] == 4]
gbc = GradientBoostingClassifier(n_estimators=250, max_depth=3, learning_rate=0.05, random_state=7).fit(tr[feat_p], tr["true_pace_class"])
gbc_raw = GradientBoostingClassifier(n_estimators=250, max_depth=3, learning_rate=0.05, random_state=7).fit(tr[feat_raw], tr["true_pace_class"])
pred = gbc.predict(te[feat_p])
pred_raw = gbc_raw.predict(te[feat_raw])
labels = ["Slow", "Normal", "Fast"]
cm = confusion_matrix(te["true_pace_class"], pred, labels=labels)
pace_metrics = dict(
    macro_f1_normalised=round(float(f1_score(te["true_pace_class"], pred, average="macro")), 4),
    macro_f1_raw_speed=round(float(f1_score(te["true_pace_class"], pred_raw, average="macro")), 4),
    confusion_labels=labels, confusion_matrix=cm.tolist(), n_test=int(len(te)),
)
trips["pace_pred"] = gbc.predict(trips[feat_p])

# ---------------------------------------------------------------- DRIVER PROFILES (what the scan card shows)
prof = trips.groupby("driver_id").agg(
    trips=("trip_id", "count"), median_pace_index=("pace_index", "median"), median_fare_ratio=("fare_ratio", "median"),
    median_v_obs=("v_obs", "median"), true_pace_class=("true_pace_class", "first"), true_fare_class=("true_fare_class", "first"),
).reset_index().merge(reg[["driver_id", "plate", "face_id"]], on="driver_id")
prof["pace_badge"] = np.select([prof["median_pace_index"] < SLOW_T, prof["median_pace_index"] > FAST_T], ["Slow", "Fast"], "Normal")
prof["fare_badge"] = np.where(prof["median_fare_ratio"] > OVER_T, "Overpriced", "Fair")
# naive alternative: judge drivers by raw speed alone (no traffic normalisation)
q_lo, q_hi = trips["v_obs"].quantile([0.125, 0.90])
prof["raw_speed_badge"] = np.select([prof["median_v_obs"] < q_lo, prof["median_v_obs"] > q_hi], ["Slow", "Fast"], "Normal")
driver_metrics = dict(
    n_drivers=int(len(prof)),
    pace_badge_accuracy=round(float((prof["pace_badge"] == prof["true_pace_class"]).mean()), 4),
    raw_speed_badge_accuracy=round(float((prof["raw_speed_badge"] == prof["true_pace_class"]).mean()), 4),
    fare_badge_accuracy=round(float((prof["fare_badge"] == prof["true_fare_class"]).mean()), 4),
)

# ---------------------------------------------------------------- SAVE
trips.to_csv(OUT / "trips_clean.csv", index=False)
prof.to_csv(OUT / "driver_profiles.csv", index=False)
te_out = te[["trip_id", "benchmark_fare_pkr"]].copy()
te_out["fair_fare_pred"] = fare_pred_te
te_out.to_csv(OUT / "fare_test_predictions.csv", index=False)
pd.DataFrame(funnel, columns=["step", "records"]).to_csv(OUT / "cleaning_funnel.csv", index=False)
metrics = dict(identity=id_metrics, walking_tail=tail_metrics, fare=fare_metrics, pace=pace_metrics, drivers=driver_metrics,
               dataset=dict(clean_trips=int(len(trips)), corridors=int(trips["corridor"].nunique()),
                            pings=int(len(pings)), median_tail_bias_kmh=round(float((trips["v_obs"] - trips["v_obs_raw"])[trips["tail_trimmed_s"] > 0].median()), 2)))
(OUT / "metrics.json").write_text(json.dumps(metrics, indent=2))
print(json.dumps(metrics, indent=2))
print(pd.DataFrame(funnel))
