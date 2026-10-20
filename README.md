# RahiScan: Automated Rickshaw Fare & Pace Telemetry

**A Data Science Lifecycle Case-Study Proposal**  
*Course: Introduction to Data Science | Submission: 21 October 2026*

---

## Team Members & Contributions

| Member | Name | University Roll No. | Primary Lifecycle Stages & Responsibilities |
| :--- | :--- | :---: | :--- |
| **Member 1** | **Muhammad Saad Hussain** | `SU92-BSCSM-F25-260` | **Define, Collect & Deploy** — Formulated the commuter case-study narrative, problem definition, curbside scanning workflow, data-collection schema, system architecture diagram, in-app deployment safeguards, and rollout roadmap. |
| **Member 2** | **Muhammad Khubaib** | `SU92-BSCSM-F25-300` | **Clean & Explore** — Built the synthetic Lahore telemetry generator, OCR + face identity fusion rules, GPS walking-tail change-point filter, and conducted the exploratory traffic-normalisation and fare-ratio analysis. |
| **Member 3** | **Huzaifa** | `SU92-BSCSM-F25-408` | **Model & Evaluate** — Built the two-tier identity and gradient-boosted regression/classification models, designed the week-4 temporal holdout evaluation and benchmark baselines, produced the publication figures, and maintained the GitHub repository. |

---

## Project Overview

Commuters in Lahore using auto-rickshaws face two everyday information gaps at the curb: vehicles operate without standardized fare meters, and passengers cannot tell before boarding whether a driver is habitually slow or simply delayed by road traffic.

**RahiScan** is a proposed crowd-sourced mobile computer vision and GPS telemetry application that addresses both problems across all seven stages of the **Data Science Lifecycle**:

1. **Define:** Translates commuter frustration into two traffic- and route-normalized metrics per ride $i$:
   - **Driving Pace Index:** $\Pi_i = \dfrac{v_{\text{obs},i}}{v_{\text{base},i}}$, comparing observed speed against the crowd-sourced median speed on the same corridor, two-hour window, and day type.
   - **Fare Fairness Ratio:** $\Phi_i = \dfrac{\text{Fare}_{\text{quoted},i}}{\widehat{\text{Fare}}_{\text{fair},i}}$, comparing the driver's quoted fare against a benchmark fair-fare prediction.
2. **Collect:** Captures a pre-boarding photo (number plate + driver face), the quoted fare in PKR, and 5-second GPS + accelerometer pings from ride initialization until arrival across eight Lahore student commuting corridors.
3. **Clean:** Removes duplicate mobile uploads, filters out missing/typo fares, fuses plate OCR ($\ge 0.85$ confidence) with driver facial embeddings ($\ge 0.70$ similarity) to disambiguate shared shift vehicles ($99.8\%$ verification precision), and trims post-arrival pedestrian **walking tails** ($v < 6\text{ km/h}$ with high step-frequency accelerometer variance) when students forget to tap *End Ride*.
4. **Explore:** Maps weekday congestion bottlenecks across corridors and hours, showing that raw velocity penalizes honest drivers caught in rush-hour gridlock while $\Pi_i$ separates true driver slowness from traffic delays.
5. **Model:** Combines MobileNetV3 + Plate OCR identity resolution with Gradient Boosted Regression Trees (`GradientBoostingRegressor` for fair fare prediction and `GradientBoostingClassifier` + 5-ride driver median aggregation for reliability badges).
6. **Evaluate:** Tests on a temporal Week-4 holdout set ($280$ unseen trips across $40$ drivers), achieving a Fair-Fare MAE of **$10.87\text{ PKR}$** (below the $15\text{ PKR}$ target) and **$100\%$ driver-level badge accuracy** when aggregated over $\ge 5$ rides.
7. **Deploy:** Returns a 2-second curbside overlay card showing verified identity, Pace Badge, and Fair-Fare range, backed by a 5-ride minimum threshold, recency weighting, monthly recalibration, and driver privacy/appeal safeguards.

---

## Repository Structure

```text
├── RahiScan_Proposal.pdf              # Compiled final PDF report (ready for submission)
├── DRAFT.tex                          # Initial draft LaTeX file
├── GUIDELINES.jfif                    # Assignment guidelines reference image
├── report/
│   ├── RahiScan_Proposal.tex          # Final publication LaTeX source (Times New Roman, 16/14/12pt)
│   ├── RahiScan_Proposal.pdf          # Compiled PDF report
│   └── figures/                       # Vector PDF charts, PNG previews & explainer illustrations
│       ├── hero_scan.jpg              # Curbside AR rickshaw scanning illustration
│       ├── data_journey.jpg           # End-to-end isometric data pipeline infographic
│       ├── app_mockup.jpg             # Three-screen mobile UI flow mockup
│       ├── fig_route_map.pdf          # Simulated 5-s GPS traces & hourly scan distribution
│       ├── fig_cleaning.pdf           # Data cleaning funnel & Plate+Face ID precision
│       ├── fig_gps_trim.pdf           # Kinematic change-point walking-tail trimmer demo
│       ├── fig_heatmap.pdf            # Corridor × hour ambient speed baseline (v_base)
│       ├── fig_explore.pdf            # Observed vs. baseline speed & bimodal Fare Ratio (Φ)
│       ├── fig_quadrant.pdf           # 40-driver behavioral profile quadrant map
│       ├── fig_evaluate.pdf           # Week-4 holdout parity plot, MAE baselines & confusion matrix
│       ├── fig_normalisation.pdf      # Traffic-normalized Π vs. raw speed ablation
│       └── fig_timeline.pdf           # Proposed 8-week execution plan
├── data/
│   ├── raw/                           # Simulated 4-week pilot raw inputs (with injected sensor noise)
│   │   ├── drivers_registry.csv       # Ground-truth registry (40 drivers across 34 rickshaws)
│   │   ├── scans.csv                  # 1,200 curbside OCR + facial similarity logs
│   │   ├── trips_raw.csv              # 1,224 raw ride submissions (including duplicates & fare typos)
│   │   ├── gps_pings.csv.gz           # 364,488 5-second GPS & accelerometer pings
│   │   └── fare_benchmarks.csv        # Reference ride-hailing quotes (inDrive / Careem / Bykea)
│   └── processed/                     # Cleaned & modeled outputs produced by src/pipeline.py
│       ├── trips_clean.csv            # 1,058 verified, tail-trimmed trips with Π and Φ features
│       ├── driver_profiles.csv        # Aggregated per-driver medians and reliability badges
│       ├── fare_test_predictions.csv  # Week-4 holdout predictions vs. benchmark fares
│       ├── cleaning_funnel.csv        # Record counts across cleaning stages
│       └── metrics.json               # Summary evaluation metrics used in the report
└── src/
    ├── generate_mock_data.py          # Generates data/raw/* (deterministic seed = 2026)
    ├── pipeline.py                    # Runs Clean -> Explore -> Model -> Evaluate -> data/processed/*
    └── make_figures.py                # Generates all vector PDF & PNG charts in report/figures/*
```

---

## Reproducing the Mock Data, Pipeline, Figures & PDF

```bash
# 1. Install Python dependencies
pip install numpy pandas scikit-learn matplotlib

# 2. Generate synthetic raw data, run the pipeline, and build all figures
python src/generate_mock_data.py
python src/pipeline.py
python src/make_figures.py

# 3. Compile the LaTeX report (using Tectonic or XeLaTeX)
cd report
tectonic -X compile RahiScan_Proposal.tex
```
