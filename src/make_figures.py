"""
RahiScan - Figure factory for the proposal report.
Reads data/processed/* and writes vector PDFs into report/figures/.

Run:  python src/make_figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
RAW, PROC, FIG = ROOT / "data" / "raw", ROOT / "data" / "processed", ROOT / "report" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

NAVY, SLATE, ORANGE, BLUE, GREEN, RED = "#14325F", "#37474F", "#D95F02", "#1B75BC", "#228B57", "#C62828"
SOFTBLUE, SOFTORANGE, LIGHT, BORDER = "#EBF3FC", "#FEF2E8", "#F5F7FA", "#BEC8D2"
CLS = {"Slow": RED, "Normal": GREEN, "Fast": BLUE}

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"], "mathtext.fontset": "stix",
    "font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold", "axes.titlecolor": NAVY,
    "axes.labelcolor": SLATE, "axes.edgecolor": BORDER, "xtick.color": SLATE, "ytick.color": SLATE,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#E3E8EE",
    "grid.linewidth": 0.6, "legend.frameon": False, "savefig.bbox": "tight", "savefig.pad_inches": 0.03,
})

trips = pd.read_csv(PROC / "trips_clean.csv", parse_dates=["start_ts"])
prof = pd.read_csv(PROC / "driver_profiles.csv")
funnel = pd.read_csv(PROC / "cleaning_funnel.csv")
fare_te = pd.read_csv(PROC / "fare_test_predictions.csv")
M = json.loads((PROC / "metrics.json").read_text())


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf")
    fig.savefig(FIG / f"{name}.png", dpi=200)
    plt.close(fig)


# 1 ---------------------------------------------------------------- route map (Collect)
pings = pd.read_csv(RAW / "gps_pings.csv.gz")
PLACES = {  # same landmark coordinates as generate_mock_data.py
    "Campus (Raiwind Rd)": (31.4010, 74.2110), "Johar Town": (31.4697, 74.2728),
    "Thokar Niaz Baig": (31.4720, 74.2420), "Township": (31.4490, 74.3080),
    "Model Town": (31.4835, 74.3260), "Kalma Chowk": (31.5040, 74.3310),
    "Gulberg (Liberty)": (31.5100, 74.3440), "Barkat Market": (31.5030, 74.3220),
    "Iqbal Town": (31.5120, 74.2930), "Mall Road": (31.5590, 74.3240),
}
fig, (ax, axh) = plt.subplots(1, 2, figsize=(7.6, 4.3), gridspec_kw={"width_ratios": [1.15, 1]})
ax.set_facecolor(LIGHT)
sample = trips.sample(160, random_state=3)
for _, r in sample.iterrows():
    g = pings[pings["trip_id"] == r.trip_id]
    ride = g[g["true_mode"] == "ride"]
    ax.plot(ride["lon"], ride["lat"], color=BLUE, alpha=0.18, lw=0.9)
    walk = g[g["true_mode"] == "walk"]
    if len(walk):
        ax.plot(walk["lon"], walk["lat"], color=RED, alpha=0.8, lw=1.2)
for name, (la, lo) in PLACES.items():
    ax.scatter(lo, la, s=46, color=ORANGE if "Campus" in name else NAVY, zorder=5, edgecolor="white", lw=1)
    off = {"Barkat Market": (-58, -16), "Kalma Chowk": (5, -11), "Gulberg (Liberty)": (-20, 7), "Thokar Niaz Baig": (-78, 5),
           "Johar Town": (5, -10), "Campus (Raiwind Rd)": (6, -4), "Iqbal Town": (-48, 6)}.get(name, (5, 4))
    ax.annotate(name, (lo, la), xytext=off, textcoords="offset points", fontsize=7.5, color=NAVY, weight="bold")
ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°N)")
ax.set_title("GPS traces (160-trip sample)")
ax.legend(handles=[plt.Line2D([], [], color=BLUE, lw=2, label="In-rickshaw ride trace"),
                   plt.Line2D([], [], color=RED, lw=2, label="Walking tail")], loc="upper left", fontsize=7.5)
ax.set_aspect(1 / np.cos(np.radians(31.47))); ax.tick_params(labelsize=8)
hrs = trips.groupby(["hour", "weekend"]).size().unstack(fill_value=0).reindex(range(24), fill_value=0)
axh.bar(hrs.index, hrs[0], color=NAVY, label="Weekday trips")
axh.bar(hrs.index, hrs.get(1, 0), bottom=hrs[0], color=ORANGE, label="Weekend trips")
axh.set_xticks(range(0, 24, 3), [f"{h:02d}" for h in range(0, 24, 3)])
axh.set_xlabel("Hour of day"); axh.set_ylabel("Clean trips logged"); axh.set_title("When riders will scan")
axh.legend(fontsize=8, loc="upper left"); axh.grid(axis="x", visible=False)
save(fig, "fig_route_map")

# 2 ---------------------------------------------------------------- GPS tail trimming (Clean)
raw_tr = pd.read_csv(RAW / "trips_raw.csv")
cand = trips[(trips["tail_trimmed_s"] > 240) & (~trips["gps_dropout"])].sort_values("duration_min").iloc[len(trips) // 400]
g = pings[pings["trip_id"] == cand.trip_id].sort_values("seq").reset_index(drop=True)
t = np.arange(len(g)) * 5 / 60
lat, lon = g["lat"].rolling(3, center=True, min_periods=1).mean(), g["lon"].rolling(3, center=True, min_periods=1).mean()
d = np.concatenate([[0], np.hypot(np.diff(lat) * 111, np.diff(lon) * 94.9)])
spd = pd.Series(d / 5 * 3600).rolling(6, center=True, min_periods=1).median()
cut_t = cand.duration_min
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 2.9), gridspec_kw={"width_ratios": [1, 1.6]})
m = t <= cut_t
a1.plot(g["lon"][m], g["lat"][m], color=BLUE, lw=1.6, label="Kept: ride")
a1.plot(g["lon"][~m], g["lat"][~m], color=RED, lw=1.6, label="Trimmed: walk")
a1.scatter(g["lon"].iloc[0], g["lat"].iloc[0], color=GREEN, zorder=5, s=30, label="Pickup")
a1.set_title("Map view"); a1.set_xticks([]); a1.set_yticks([]); a1.legend(fontsize=7.5, loc="best")
a2.axvspan(cut_t, t[-1], color=SOFTORANGE)
a2.plot(t, spd, color=NAVY, lw=1.1)
a2.axhline(6, color=RED, ls="--", lw=1); a2.text(0.3, 7.2, "6 km/h walking threshold", color=RED, fontsize=8)
a2.axvline(cut_t, color=ORANGE, lw=1.5)
a2.text(cut_t + 0.2, spd.max() * 0.85, "change-point:\ntail trimmed", color=ORANGE, fontsize=8.5, weight="bold")
a2.set_xlabel("Minutes since ride initialised"); a2.set_ylabel("Speed (km/h)"); a2.set_title("Speed trace with walking tail")
raw_v, clean_v = cand.v_obs_raw, cand.v_obs
fig.suptitle(f"Trip {cand.trip_id}: average speed corrected from {raw_v:.1f} to {clean_v:.1f} km/h after trimming",
             fontsize=10, color=SLATE, y=1.02)
save(fig, "fig_gps_trim")

# 3 ---------------------------------------------------------------- cleaning funnel + identity (Clean)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 2.7), gridspec_kw={"width_ratios": [1.55, 1]})
f = funnel.iloc[:-1]
cols = [NAVY, BLUE, BLUE, BLUE, GREEN]
a1.barh(f["step"][::-1], f["records"][::-1], color=cols[::-1], height=0.62)
for i, v in enumerate(f["records"][::-1]):
    a1.text(v - 8, i, f"{v:,}", va="center", ha="right", color="white", fontsize=9, weight="bold")
a1.set_xlim(900, 1250); a1.grid(axis="y", visible=False); a1.set_title("Cleaning funnel (records kept)")
a1.tick_params(axis="y", labelsize=8.5)
idm = M["identity"]
x = np.arange(2); w = 0.36
a2.bar(x - w / 2, [idm["id_plate_only"]["coverage"] * 100, idm["id_fused"]["coverage"] * 100], w, color=BORDER, label="Coverage")
a2.bar(x + w / 2, [idm["id_plate_only"]["precision"] * 100, idm["id_fused"]["precision"] * 100], w, color=[ORANGE, GREEN], label="Precision")
for xi, v in zip(x + w / 2, [idm["id_plate_only"]["precision"] * 100, idm["id_fused"]["precision"] * 100]):
    a2.text(xi, v + 0.6, f"{v:.1f}%", ha="center", fontsize=8.5, weight="bold", color=NAVY)
a2.set_xticks(x, ["Plate OCR only", "Plate + Face"]); a2.set_ylim(75, 106); a2.set_ylabel("%")
for xi, v in zip(x - w / 2, [idm["id_plate_only"]["coverage"] * 100, idm["id_fused"]["coverage"] * 100]):
    a2.text(xi, v + 0.6, f"{v:.1f}%", ha="center", fontsize=8, color=SLATE)
a2.set_title("Driver identification"); a2.legend(fontsize=7.5, loc="upper left", ncol=2); a2.grid(axis="x", visible=False)
save(fig, "fig_cleaning")

# 4 ---------------------------------------------------------------- corridor x hour heatmap (Explore)
hm = trips[trips["weekend"] == 0].pivot_table(index="corridor", columns="hour_bucket", values="v_base", aggfunc="median")
cmap = LinearSegmentedColormap.from_list("rs", [RED, "#F6C28B", "#DCEFE3", GREEN])
fig, ax = plt.subplots(figsize=(7.4, 2.9))
ax.grid(False)
im = ax.imshow(hm.values, aspect="auto", cmap=cmap, vmin=10, vmax=32)
ax.set_xticks(range(hm.shape[1]), [f"{int(h):02d}:00" for h in hm.columns], fontsize=8)
ax.set_yticks(range(hm.shape[0]), hm.index, fontsize=8.5)
for i in range(hm.shape[0]):
    for j in range(hm.shape[1]):
        v = hm.values[i, j]
        if not np.isnan(v):
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7.5, color="white" if v < 15 or v > 28 else NAVY)
cb = fig.colorbar(im, ax=ax, pad=0.01); cb.set_label("km/h", color=SLATE); cb.outline.set_visible(False)
ax.set_title("Crowd-sourced ambient baseline speed $v_{base}$ by corridor and hour (weekdays)")
save(fig, "fig_heatmap")

# 5 ---------------------------------------------------------------- v_obs vs v_base scatter + Phi histogram (Explore)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.1))
for c in ["Normal", "Fast", "Slow"]:
    s = trips[trips["pace_label"] == c]
    a1.scatter(s["v_base"], s["v_obs"], s=9, alpha=0.6, color=CLS[c], label=f"{c} ($\\Pi$ {'< 0.75' if c=='Slow' else '> 1.15' if c=='Fast' else 'in band'})", edgecolor="none")
xx = np.linspace(8, 34, 10)
a1.fill_between(xx, 0.75 * xx, 1.15 * xx, color=SOFTBLUE, zorder=0)
a1.plot(xx, xx, color=NAVY, ls="--", lw=1); a1.text(31, 25, "$\\Pi = 1$", color=NAVY, fontsize=9)
a1.set_xlabel("Ambient baseline $v_{base}$ (km/h)"); a1.set_ylabel("Observed $v_{obs}$ (km/h)")
a1.set_title("Speed is judged against traffic"); a1.legend(fontsize=7.5, loc="upper left", markerscale=1.8)
a1.set_xlim(8, 34); a1.set_ylim(0, 45)
bins = np.linspace(0.6, 2.2, 41)
a2.hist(trips["fare_ratio"], bins=bins, color=BLUE, alpha=0.85)
a2.hist(trips.loc[trips["fare_ratio"] > 1.25, "fare_ratio"], bins=bins, color=RED, alpha=0.9)
a2.axvline(1.25, color=RED, ls="--", lw=1); a2.text(1.28, a2.get_ylim()[1] * 0.85, "Overpriced\n$\\Phi > 1.25$", color=RED, fontsize=8.5)
a2.axvline(1.0, color=NAVY, ls=":", lw=1)
a2.set_xlabel("Fare Fairness Ratio $\\Phi$ = quoted / fair"); a2.set_ylabel("Trips"); a2.set_title("Quoted fares split into two groups")
save(fig, "fig_explore")

# 6 ---------------------------------------------------------------- driver quadrant (Model / Deploy)
fig, ax = plt.subplots(figsize=(7.4, 3.9))
ax.axvspan(0.4, 0.75, color=SOFTORANGE, zorder=0); ax.axhspan(1.25, 2.1, color="#FBE9E9", zorder=0)
ax.axvline(0.75, color=RED, ls="--", lw=0.9); ax.axvline(1.15, color=BLUE, ls="--", lw=0.9); ax.axhline(1.25, color=RED, ls="--", lw=0.9)
colors = [RED if (p < 0.75 and f > 1.25) else ORANGE if (p < 0.75 or f > 1.25) else BLUE if p > 1.15 else GREEN
          for p, f in zip(prof["median_pace_index"], prof["median_fare_ratio"])]
ax.scatter(prof["median_pace_index"], prof["median_fare_ratio"], s=prof["trips"] * 4, c=colors, alpha=0.85, edgecolor="white", lw=1)
for _, r in prof.iterrows():
    if r.median_pace_index < 0.75 or r.median_fare_ratio > 1.85 or r.median_pace_index > 1.2 and r.median_fare_ratio < 1.04:
        ax.annotate(r.plate, (r.median_pace_index, r.median_fare_ratio), xytext=(6, -3), textcoords="offset points", fontsize=7.5, color=SLATE)
ax.text(0.42, 2.02, "SLOW & OVERPRICED", color=RED, weight="bold", fontsize=9)
ax.text(0.78, 2.02, "OVERPRICED", color=ORANGE, weight="bold", fontsize=9)
ax.text(0.42, 0.83, "SLOW", color=ORANGE, weight="bold", fontsize=9)
ax.text(0.80, 0.83, "FAIR & NORMAL PACE", color=GREEN, weight="bold", fontsize=9)
ax.text(1.17, 0.83, "FAST", color=BLUE, weight="bold", fontsize=9)
ax.set_xlim(0.4, 1.4); ax.set_ylim(0.8, 2.1)
ax.set_xlabel("Driver median Pace Index $\\Pi$"); ax.set_ylabel("Driver median Fare Ratio $\\Phi$")
ax.set_title("Driver profiles after four simulated weeks (bubble size = trips logged)")
save(fig, "fig_quadrant")

# 7 ---------------------------------------------------------------- evaluation (Evaluate)
fig, axs = plt.subplots(1, 3, figsize=(7.8, 2.8), gridspec_kw={"width_ratios": [1.1, 0.9, 1.0], "wspace": 0.55})
a = axs[0]
a.scatter(fare_te["benchmark_fare_pkr"], fare_te["fair_fare_pred"], s=8, color=BLUE, alpha=0.6, edgecolor="none")
lim = [fare_te["benchmark_fare_pkr"].min() - 10, fare_te["benchmark_fare_pkr"].max() + 10]
a.plot(lim, lim, color=NAVY, ls="--", lw=1); a.set_xlim(lim); a.set_ylim(lim)
a.set_xlabel("Benchmark fare (PKR)"); a.set_ylabel("Predicted fair fare (PKR)"); a.set_title("Fare model, week-4 holdout")
a.text(0.05, 0.88, f"MAE = {M['fare']['gbr_mae']:.1f} PKR", transform=a.transAxes, color=GREEN, weight="bold", fontsize=9)
a = axs[1]
names = ["Flat\nrate", "Linear\n(distance)", "Gradient\nBoosting"]
vals = [M["fare"]["flat_rate_mae"], M["fare"]["linear_distance_only_mae"], M["fare"]["gbr_mae"]]
b = a.bar(names, vals, color=[BORDER, BLUE, GREEN], width=0.6); a.set_yscale("log")
for rect, v in zip(b, vals):
    a.text(rect.get_x() + rect.get_width() / 2, v * 1.08, f"{v:.1f}", ha="center", fontsize=8.5, weight="bold", color=NAVY)
a.axhline(15, color=RED, ls="--", lw=1); a.text(2.35, 16.5, "target\n< 15", color=RED, fontsize=7.5, ha="right")
a.set_title("Fare MAE (PKR, log)"); a.grid(axis="x", visible=False); a.tick_params(axis="x", labelsize=8)
a = axs[2]
cm = np.array(M["pace"]["confusion_matrix"]); lab = M["pace"]["confusion_labels"]
a.grid(False)
a.imshow(cm / cm.sum(axis=1, keepdims=True), cmap=LinearSegmentedColormap.from_list("b", ["white", NAVY]), vmin=0, vmax=1)
for i in range(3):
    for j in range(3):
        a.text(j, i, cm[i, j], ha="center", va="center", fontsize=9, weight="bold", color="white" if cm[i, j] / cm[i].sum() > 0.5 else NAVY)
a.set_xticks(range(3), lab, fontsize=8); a.set_yticks(range(3), lab, fontsize=8)
a.set_xlabel("Predicted"); a.set_ylabel("True driver class"); a.set_title("Pace classifier")
save(fig, "fig_evaluate")

# 8 ---------------------------------------------------------------- normalisation benefit (Evaluate)
fig, ax = plt.subplots(figsize=(7.4, 2.3))
grp = ["Single-trip macro $F_1$", "Driver badge accuracy"]
raw = [M["pace"]["macro_f1_raw_speed"], M["drivers"]["raw_speed_badge_accuracy"]]
norm = [M["pace"]["macro_f1_normalised"], M["drivers"]["pace_badge_accuracy"]]
y = np.arange(2); h = 0.36
ax.barh(y + h / 2, raw, h, color=BORDER, label="Raw speed only (no traffic context)")
ax.barh(y - h / 2, norm, h, color=GREEN, label="Traffic-normalised Pace Index $\\Pi$")
for yi, v in zip(list(y + h / 2) + list(y - h / 2), raw + norm):
    ax.text(v + 0.01, yi, f"{v:.2f}", va="center", fontsize=9, weight="bold", color=NAVY)
ax.set_yticks(y, grp); ax.set_xlim(0, 1.12); ax.invert_yaxis(); ax.grid(axis="y", visible=False)
ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2); ax.set_title("Why normalising against traffic matters")
save(fig, "fig_normalisation")

# 9 ---------------------------------------------------------------- proposed timeline (Deploy)
tasks = [("Define metrics & ethics approval", 0, 1, NAVY), ("App prototype (scan + tracker)", 0.5, 2, BLUE),
         ("Collect: 4-week field pilot", 2, 4, BLUE), ("Clean & explore (rolling)", 2.5, 4.5, ORANGE),
         ("Model training & tuning", 4, 5.5, ORANGE), ("Evaluate on week-4 holdout", 5.5, 6.2, GREEN),
         ("Deploy campus beta", 6.2, 7.5, GREEN)]
fig, ax = plt.subplots(figsize=(7.4, 2.4))
for i, (n, s, e, c) in enumerate(tasks):
    ax.barh(i, e - s, left=s, color=c, height=0.6)
ax.set_yticks(range(len(tasks)), [t[0] for t in tasks], fontsize=8.5); ax.invert_yaxis(); ax.set_xlim(0, 8)
ax.set_xticks(np.arange(8) + 0.5, [f"Wk {k+1}" for k in range(8)], fontsize=8.5); ax.tick_params(axis="x", length=0)
ax.set_xticks(range(9), minor=True); ax.grid(axis="x", which="major", visible=False); ax.grid(axis="x", which="minor", visible=True); ax.grid(axis="y", visible=False)
ax.set_title("Proposed eight-week execution plan")
save(fig, "fig_timeline")
print("figures written to", FIG)
