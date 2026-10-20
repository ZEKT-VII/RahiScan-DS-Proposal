"""
RahiScan - Mock data generator
==============================

Creates a fully synthetic (mock) dataset that mirrors what the proposed
RahiScan app would collect during a four-week pilot in Lahore:

    data/raw/drivers_registry.csv   -> hidden "ground truth" driver/vehicle registry (simulation only)
    data/raw/scans.csv              -> one row per curb-side photo scan (OCR + face match output)
    data/raw/trips_raw.csv          -> one row per ride submission (fare quote, timestamps, flags)
    data/raw/gps_pings.csv.gz       -> 5-second GPS pings for every ride (incl. walking tails, dropouts)
    data/raw/fare_benchmarks.csv    -> reference fares for the same trip from ride-hailing quotes

Every record is SIMULATED. Real-world noise (blurry plates, forgotten
"End Ride" taps, GPS dropouts, duplicate uploads, fare typos) is injected
on purpose so the cleaning stage of the lifecycle has something to fix.

Run:  python src/generate_mock_data.py
"""
from __future__ import annotations

import math
import string
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 2026
rng = np.random.default_rng(SEED)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Geography: approximate Lahore landmarks (lat, lon)
# ---------------------------------------------------------------------------
PLACES = {
    "Campus (Raiwind Rd)": (31.4010, 74.2110),
    "Johar Town": (31.4697, 74.2728),
    "Thokar Niaz Baig": (31.4720, 74.2420),
    "Township": (31.4490, 74.3080),
    "Model Town": (31.4835, 74.3260),
    "Kalma Chowk": (31.5040, 74.3310),
    "Gulberg (Liberty)": (31.5100, 74.3440),
    "Barkat Market": (31.5030, 74.3220),
    "Iqbal Town": (31.5120, 74.2930),
    "Mall Road": (31.5590, 74.3240),
}

# corridor -> (origin, destination, free-flow speed km/h, congestion sensitivity)
CORRIDORS = {
    "C1 Johar Town - Campus": ("Johar Town", "Campus (Raiwind Rd)", 29.0, 0.85),
    "C2 Thokar - Campus": ("Thokar Niaz Baig", "Campus (Raiwind Rd)", 31.0, 0.70),
    "C3 Township - Campus": ("Township", "Campus (Raiwind Rd)", 28.0, 0.90),
    "C4 Kalma - Gulberg": ("Kalma Chowk", "Gulberg (Liberty)", 24.0, 1.05),
    "C5 Model Town - Township": ("Model Town", "Township", 25.0, 0.95),
    "C6 Barkat - Iqbal Town": ("Barkat Market", "Iqbal Town", 24.5, 1.00),
    "C7 Mall Road - Gulberg": ("Mall Road", "Gulberg (Liberty)", 23.0, 1.25),
    "C8 Iqbal Town - Johar Town": ("Iqbal Town", "Johar Town", 27.0, 0.90),
}
CORRIDOR_WEIGHTS = np.array([0.20, 0.12, 0.13, 0.13, 0.11, 0.10, 0.10, 0.11])


def haversine_km(a, b):
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def congestion(hour: float, weekday: int) -> float:
    """Congestion level tau in [0, ~0.65] by time of day (two rush-hour peaks)."""
    morning = 0.55 * math.exp(-((hour - 8.3) ** 2) / (2 * 1.0**2))
    evening = 0.60 * math.exp(-((hour - 17.5) ** 2) / (2 * 1.4**2))
    midday = 0.25 * math.exp(-((hour - 13.0) ** 2) / (2 * 2.0**2))
    tau = 0.05 + morning + evening + midday
    if weekday >= 5:  # weekend relief
        tau *= 0.6
    return min(tau, 0.75)


# ---------------------------------------------------------------------------
# 2. Driver & vehicle registry (hidden ground truth)
# ---------------------------------------------------------------------------
N_DRIVERS = 40
N_SHARED = 6  # vehicles rented by two drivers on different shifts


def make_plate() -> str:
    series = rng.choice(["LEP", "LEA", "LEB", "LER", "LES"])
    return f"{series}-{rng.integers(1000, 9999)}"


plates = []
while len(plates) < N_DRIVERS - N_SHARED:
    p = make_plate()
    if p not in plates:
        plates.append(p)

drivers = []
for i in range(N_DRIVERS):
    plate = plates[i] if i < len(plates) else plates[i - len(plates)]  # last 6 share
    r = rng.random()
    if r < 0.125:
        pace_class, pace = "Slow", rng.uniform(0.50, 0.70)
    elif r < 0.225:
        pace_class, pace = "Fast", rng.uniform(1.18, 1.32)
    else:
        pace_class, pace = "Normal", rng.normal(1.0, 0.06)
    over = rng.uniform(1.40, 1.90) if (rng.random() < 0.28 or pace_class == "Slow" and rng.random() < 0.6) else rng.normal(1.04, 0.05)
    drivers.append(
        dict(
            driver_id=f"D{i+1:02d}",
            face_id=f"F{i+1:02d}",
            plate=plate,
            shift="Evening" if i >= len(plates) else "Day",
            true_pace_multiplier=round(pace, 3),
            true_pace_class=pace_class,
            true_overcharge_factor=round(over, 3),
            true_fare_class="Overpriced" if over > 1.25 else "Fair",
        )
    )
drivers_df = pd.DataFrame(drivers)
drivers_df.to_csv(RAW / "drivers_registry.csv", index=False)

# ---------------------------------------------------------------------------
# 3. Trips, scans, GPS pings, fare benchmarks
# ---------------------------------------------------------------------------
N_TRIPS = 1200
N_USERS = 85
START = datetime(2026, 11, 2)  # proposed pilot window: 2 Nov - 29 Nov 2026
PING_S = 5

HOUR_PROBS = np.array([0.2, 0.1, 0.1, 0.1, 0.2, 0.6, 2.0, 6.5, 9.0, 6.0, 3.0, 3.0,
                       4.0, 5.0, 5.5, 5.5, 6.5, 7.0, 6.0, 4.0, 3.0, 2.0, 1.0, 0.5])
HOUR_PROBS /= HOUR_PROBS.sum()


def misread(plate: str) -> str:
    """Simulate an OCR error on a dented / glared plate."""
    swaps = {"8": "B", "0": "O", "1": "I", "5": "S", "2": "Z", "B": "8", "S": "5"}
    chars = list(plate)
    idx = [k for k, c in enumerate(chars) if c in swaps]
    if idx:
        k = rng.choice(idx)
        chars[k] = swaps[chars[k]]
    else:
        k = rng.integers(4, len(chars))
        chars[k] = rng.choice(list(string.digits))
    return "".join(chars)


def build_path(o, d, n_way=3):
    """Polyline from o to d through jittered waypoints (fake road geometry)."""
    pts = [np.array(o)]
    for k in range(1, n_way + 1):
        t = k / (n_way + 1)
        base = np.array(o) * (1 - t) + np.array(d) * t
        pts.append(base + rng.normal(0, 0.004, 2))
    pts.append(np.array(d))
    return np.array(pts)


def walk_along(path, dist_km):
    """Return lat/lon at cumulative distances dist_km along the polyline."""
    seg = [haversine_km(path[i], path[i + 1]) for i in range(len(path) - 1)]
    cum = np.concatenate([[0], np.cumsum(seg)])
    dist_km = np.clip(dist_km, 0, cum[-1])
    lat = np.interp(dist_km, cum, path[:, 0])
    lon = np.interp(dist_km, cum, path[:, 1])
    return lat, lon, cum[-1]


driver_trip_weights = rng.dirichlet(np.ones(N_DRIVERS) * 2.5)

trips, scans, pings, bench = [], [], [], []
corr_names = list(CORRIDORS.keys())

for t in range(N_TRIPS):
    trip_id = f"TR-{t+1:04d}"
    drv = drivers_df.iloc[rng.choice(N_DRIVERS, p=driver_trip_weights)]
    cname = corr_names[rng.choice(len(corr_names), p=CORRIDOR_WEIGHTS)]
    o_name, d_name, v_free, sens = CORRIDORS[cname]
    o, d = PLACES[o_name], PLACES[d_name]
    if rng.random() < 0.5:
        o, d, o_name, d_name = d, o, d_name, o_name

    day = int(rng.integers(0, 28))
    hour_int = int(rng.choice(24, p=HOUR_PROBS))
    if drv["shift"] == "Evening" and hour_int < 14:
        hour_int = int(rng.integers(14, 23))
    elif drv["shift"] == "Day" and hour_int >= 21:
        hour_int = int(rng.integers(6, 20))
    start_ts = START + timedelta(days=day, hours=hour_int, minutes=int(rng.integers(0, 60)), seconds=int(rng.integers(0, 60)))
    weekday = start_ts.weekday()
    hour = start_ts.hour + start_ts.minute / 60
    tau = congestion(hour, weekday)

    path = build_path(o, d)
    _, _, path_km = walk_along(path, np.array([0.0]))
    v_base_true = v_free * (1 - tau * sens)
    v_obs_true = float(np.clip(v_base_true * drv.true_pace_multiplier * rng.normal(1, 0.06), 4.5, 45))
    ride_s = path_km / v_obs_true * 3600

    # --- speed profile with signal stops, rescaled to hit target average ---
    n = int(math.ceil(ride_s / PING_S)) + 1
    prof = np.clip(rng.normal(1.0, 0.18, n), 0.3, 1.8)
    prof = np.convolve(prof, np.ones(5) / 5, mode="same")
    for _ in range(int(rng.integers(1, 5))):  # traffic-signal stops
        s0 = int(rng.integers(2, max(3, n - 10)))
        prof[s0 : s0 + int(rng.integers(3, 15))] = 0.0
    prof[0], prof[-1] = 0.0, 0.0
    step_km = prof / prof.sum() * path_km
    cum_km = np.concatenate([[0], np.cumsum(step_km[1:])])
    lat, lon, _ = walk_along(path, cum_km)
    secs = np.arange(len(cum_km)) * PING_S
    mode = np.array(["ride"] * len(cum_km), dtype=object)

    # --- walking tail: user forgot to press "End Ride" (~13 %) ---
    forgot = rng.random() < 0.13
    tail_s = 0
    if forgot:
        tail_s = int(rng.integers(120, 600))
        m = tail_s // PING_S
        heading = rng.uniform(0, 2 * math.pi)
        walk_kmh = rng.uniform(3.5, 5.5)
        step = walk_kmh / 3600 * PING_S
        dlat = step / 111.0 * math.cos(heading) * np.abs(rng.normal(1, 0.3, m))
        dlon = step / (111.0 * math.cos(math.radians(d[0]))) * math.sin(heading) * np.abs(rng.normal(1, 0.3, m))
        lat = np.concatenate([lat, lat[-1] + np.cumsum(dlat)])
        lon = np.concatenate([lon, lon[-1] + np.cumsum(dlon)])
        secs = np.concatenate([secs, secs[-1] + PING_S * np.arange(1, m + 1)])
        mode = np.concatenate([mode, np.array(["walk"] * m, dtype=object)])

    # --- GPS noise (+-6 m) and dropouts in tunnels/underpasses (~6 %) ---
    lat = lat + rng.normal(0, 6 / 111000, len(lat))
    lon = lon + rng.normal(0, 6 / 94000, len(lon))
    keep = np.ones(len(lat), bool)
    dropout = rng.random() < 0.06
    if dropout and len(lat) > 40:
        g0 = int(rng.integers(5, len(lat) - 30))
        keep[g0 : g0 + int(rng.integers(15, int(len(lat) * 0.35) + 16))] = False
    # phone in hand -> strong step signal; phone in a bag (~12 % of tails) -> weak step signal
    walk_acc = 0.8 if rng.random() < 0.12 else 1.6
    accel_var = np.where(mode == "walk", rng.normal(walk_acc, 0.3, len(lat)), rng.normal(0.35, 0.12, len(lat)))
    for k in np.where(keep)[0]:
        pings.append((trip_id, int(k), (start_ts + timedelta(seconds=int(secs[k]))).isoformat(),
                      round(float(lat[k]), 6), round(float(lon[k]), 6), round(float(abs(accel_var[k])), 3), mode[k]))

    # --- fares ---
    fair_true = 70 + 42 * path_km * (1 + 0.25 * tau)
    benchmark = round(fair_true * rng.normal(1, 0.03) / 5) * 5
    quoted = round(fair_true * drv.true_overcharge_factor * rng.normal(1, 0.04) / 10) * 10
    fare_issue = "ok"
    r = rng.random()
    if r < 0.03:
        quoted, fare_issue = np.nan, "missing"
    elif r < 0.04:
        quoted, fare_issue = quoted * 10, "typo_extra_zero"

    # --- scan: OCR + face matching ---
    low_light = (start_ts.hour >= 18 or start_ts.hour < 6) and rng.random() < 0.45 or rng.random() < 0.06
    ocr_conf = float(np.clip(rng.normal(0.62, 0.12) if low_light else rng.normal(0.94, 0.03), 0.2, 0.995))
    ocr_text = misread(drv.plate) if ocr_conf < 0.85 and rng.random() < 0.7 else drv.plate
    face_visible = rng.random() > (0.25 if low_light else 0.05)
    face_score = float(np.clip(rng.normal(0.84, 0.06), 0, 1)) if face_visible else float(np.clip(rng.normal(0.45, 0.12), 0, 1))
    face_pred = drv.face_id if face_score >= 0.70 else f"F{rng.integers(1, N_DRIVERS+1):02d}"
    if face_visible and rng.random() < 0.025:  # look-alike false match
        face_pred = f"F{rng.integers(1, N_DRIVERS+1):02d}"

    scans.append(dict(scan_id=f"SC-{t+1:04d}", trip_id=trip_id, scan_ts=(start_ts - timedelta(seconds=int(rng.integers(40, 240)))).isoformat(),
                      ocr_plate_text=ocr_text, ocr_confidence=round(ocr_conf, 3), face_match_id=face_pred,
                      face_similarity=round(face_score, 3), low_light=bool(low_light),
                      true_driver_id=drv.driver_id))
    end_ts = start_ts + timedelta(seconds=int(secs[-1]))
    trips.append(dict(trip_id=trip_id, user_id=f"U{rng.integers(1, N_USERS+1):03d}", corridor=cname,
                      origin=o_name, destination=d_name, start_ts=start_ts.isoformat(), end_ts=end_ts.isoformat(),
                      weekday=weekday, quoted_fare_pkr=quoted, end_ride_pressed=not forgot,
                      gps_dropout=bool(dropout), true_driver_id=drv.driver_id, true_tail_s=tail_s, fare_issue=fare_issue))
    bench.append(dict(trip_id=trip_id, benchmark_fare_pkr=benchmark, source=rng.choice(["inDrive", "Careem", "Bykea"])))

trips_df = pd.DataFrame(trips)
# --- duplicate uploads from flaky mobile data (~2 %) ---
dups = trips_df.sample(frac=0.02, random_state=SEED).copy()
dups["start_ts"] = pd.to_datetime(dups["start_ts"]) + pd.to_timedelta(rng.integers(0, 3, len(dups)), unit="s")
dups["start_ts"] = dups["start_ts"].dt.strftime("%Y-%m-%dT%H:%M:%S")
trips_df = pd.concat([trips_df, dups]).sort_values("start_ts").reset_index(drop=True)

trips_df.to_csv(RAW / "trips_raw.csv", index=False)
pd.DataFrame(scans).to_csv(RAW / "scans.csv", index=False)
pd.DataFrame(bench).to_csv(RAW / "fare_benchmarks.csv", index=False)
pd.DataFrame(pings, columns=["trip_id", "seq", "ts", "lat", "lon", "accel_var", "true_mode"]).to_csv(
    RAW / "gps_pings.csv.gz", index=False, compression="gzip")

print(f"drivers={len(drivers_df)} trips(raw rows)={len(trips_df)} scans={len(scans)} pings={len(pings)}")
