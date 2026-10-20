"""
Generate individual student viva & presentation study guide PDFs for RahiScan.
Outputs:
  - study_guides/Study_Guide_Saad_Hussain.pdf  (Member 1: Define, Collect, Deploy)
  - study_guides/Study_Guide_Khubaib.pdf       (Member 2: Clean, Explore)
  - study_guides/Study_Guide_Huzaifa.pdf       (Member 3: Model, Evaluate)
Also copies them to workspace root for quick student access.
"""

from pathlib import Path
import subprocess
import shutil
import pymupdf

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "study_guides"
OUT_DIR.mkdir(parents=True, exist_ok=True)

COMMON_PREAMBLE = r"""\documentclass[10pt, a4paper]{article}
\usepackage[a4paper, top=1.3cm, bottom=1.3cm, left=1.35cm, right=1.35cm,
            headheight=20pt, headsep=7pt, footskip=13pt]{geometry}

\usepackage{amsmath,amssymb}
\usepackage{fontspec}
\IfFileExists{fonts/times.ttf}{%
  \setmainfont{times.ttf}[Path=fonts/, BoldFont=timesbd.ttf,
                          ItalicFont=timesi.ttf, BoldItalicFont=timesbi.ttf]%
}{%
  \setmainfont{TeX Gyre Termes}%
}

\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{colortbl}
\usepackage{fancyhdr}
\usepackage{lastpage}
\usepackage{titlesec}
\usepackage[most]{tcolorbox}
\usepackage[hidelinks]{hyperref}

% IEEE / Nature / Viridis Scientific Palette
\definecolor{navyblue}{HTML}{1B365D}
\definecolor{slate}{HTML}{334155}
\definecolor{softblue}{HTML}{EBF2F7}
\definecolor{softteal}{HTML}{E6F2F2}
\definecolor{softred}{HTML}{F9EBEB}
\definecolor{accentteal}{HTML}{1F7A7A}
\definecolor{accentblue}{HTML}{2B6CB0}
\definecolor{accentred}{HTML}{A82020}
\definecolor{lightgray}{HTML}{F8FAFC}
\definecolor{bordergray}{HTML}{94A3B8}

\titleformat{\section}{\fontsize{11.5pt}{13.5pt}\selectfont\bfseries\color{navyblue}}
  {\thesection.}{0.3em}{}[{\color{accentteal}\titlerule[0.7pt]}]
\titleformat{\subsection}{\fontsize{10pt}{12pt}\selectfont\bfseries\color{accentblue}}{\thesubsection}{0.3em}{}

\titlespacing*{\section}{0pt}{2.5pt}{1.5pt}
\titlespacing*{\subsection}{0pt}{1.5pt}{1pt}

\setlength{\parindent}{0pt}
\setlength{\parskip}{1.2pt}
\linespread{0.97}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\fontsize{8pt}{10pt}\selectfont\color{navyblue}\textbf{RahiScan Viva Study Guide} \(\cdot\) \textcolor{accentblue}{__STUDENT_NAME__ (__ROLL_NO__)}}
\fancyhead[R]{\fontsize{8pt}{10pt}\selectfont\color{slate}Intro to Data Science \(\cdot\) Fall 2026}
\fancyfoot[L]{\fontsize{7.5pt}{9.5pt}\selectfont\color{slate}Superior University Gold Campus \(\cdot\) Group Proposal Defense}
\fancyfoot[R]{\fontsize{8pt}{10pt}\selectfont\color{navyblue}\textbf{Page \thepage\ of \pageref{LastPage}}}
\renewcommand{\headrule}{{\color{accentteal}\hrule height 0.6pt}}
\renewcommand{\footrule}{{\color{bordergray}\hrule height 0.5pt}}

\newtcolorbox{qa}[1][]{enhanced, colback=lightgray, colframe=navyblue, boxrule=0.5pt,
  arc=2.5pt, left=6pt, right=6pt, top=2.5pt, bottom=2.5pt, fonttitle=\bfseries\footnotesize,
  coltitle=white, colbacktitle=navyblue, title={#1}, before skip=1.5pt, after skip=1.5pt}

\newtcolorbox{speaking}[1][]{enhanced, colback=softblue, colframe=accentblue, boxrule=0.5pt,
  arc=2.5pt, left=6pt, right=6pt, top=2.5pt, bottom=2.5pt, fonttitle=\bfseries\footnotesize,
  coltitle=white, colbacktitle=accentblue, title={#1}, before skip=1.5pt, after skip=1.5pt}

\newtcolorbox{overviewbox}[1][]{enhanced, colback=softteal, colframe=accentteal, boxrule=0.5pt,
  arc=2.5pt, left=6pt, right=6pt, top=2.5pt, bottom=2.5pt, fonttitle=\bfseries\footnotesize,
  coltitle=white, colbacktitle=accentteal, title={#1}, before skip=1.5pt, after skip=1.5pt}

\begin{document}
"""

SAAD_TEX = COMMON_PREAMBLE.replace("__STUDENT_NAME__", "Muhammad Saad Hussain").replace("__ROLL_NO__", "SU92-BSCSM-F25-260") + r"""
% Top Banner
\begin{tcolorbox}[enhanced, colback=navyblue, colframe=navyblue, arc=3pt, left=8pt, right=8pt, top=4pt, bottom=4pt]
  {\fontsize{15pt}{17pt}\selectfont\color{white}\bfseries RahiScan \(\cdot\) Student Viva Study Guide}\\[1.5pt]
  {\fontsize{10pt}{12pt}\selectfont\color{softteal}\textbf{Member 1: Muhammad Saad Hussain} (Roll No: \texttt{SU92-BSCSM-F25-260})}\\[1pt]
  {\fontsize{8.5pt}{10.5pt}\selectfont\color{white!85!softblue}\textbf{Assigned Role:} Architect \& Product Lead \(\cdot\) \textbf{Primary Stages:} Case Study, Define, Collect, Deploy}
\end{tcolorbox}

\begin{overviewbox}[Quick 30-Second Group Overview (All Members Must Know This)]
\footnotesize
\begin{itemize}\setlength{\itemsep}{0.8pt}\setlength{\parskip}{0pt}
  \item \textbf{What is RahiScan?} A crowd-sourced mobile app proposal for students commuting by \textbf{Qingqi rickshaw} to \textbf{Superior University Gold Campus} (Raiwind Road) and across Lahore corridors.
  \item \textbf{The Core Problem:} Qingqi rickshaws lack fare meters. Curbside passengers face two unknowns: (1) Is the quoted fare fair or inflated? (2) Is the driver normal or habitually slow?
  \item \textbf{How It Works:} Snap one photo before boarding. The app reads the \textbf{number plate} and \textbf{driver's face}, checks past logs, and returns a scorecard in \textbf{\(< 2\) seconds}. During the trip, it logs 5-second GPS telemetry.
  \item \textbf{Status:} Comprehensive research proposal backed by a 4-week simulated pilot (\textbf{1,224 rides}, \textbf{40 drivers}).
\end{itemize}
\end{overviewbox}

\begin{tcolorbox}[enhanced, colback=white, colframe=bordergray, boxrule=0.4pt, arc=2.5pt, left=6pt, right=6pt, top=2.5pt, bottom=2.5pt]
  \footnotesize \textbf{Your Role in Simple Words:} You open the group viva by setting the scene: narrating our morning commute story, explaining how we converted commuter frustration into quantitative metrics (\textbf{Define}), describing how data is collected with biometric privacy safeguards (\textbf{Collect}), and concluding with how the app is safely deployed at the roadside (\textbf{Deploy}).
\end{tcolorbox}

\section{What to Say: Step-by-Step Viva Presentation Script}

\subsection{A. The Case Study Story \& Lifecycle Mapping (Report Page 2)}
\begin{speaking}[Speaking Script: Case Study Story]
\footnotesize
``Our project originated from a real Monday morning commute at 7:40 AM from Johar Town to an 8:30 AM lab at \textbf{Superior University Gold Campus} on Raiwind Road (9.6 km away). The first Qingqi driver quoted \textbf{140 PKR}; we bargained down to \textbf{110 PKR} and boarded. He crawled along the left lane and stopped for tea at a dhaba, making us twelve minutes late. The next morning, a different driver completed the identical trip for the standard \textbf{80 PKR} in twenty minutes despite heavier traffic (similarly, \textbf{Raiwind to Gold Campus} is \textbf{120 PKR} for 16.1 km, and inner-city trips are 40--85 PKR).

From the curb, both Qingqis looked identical. We designed \textbf{RahiScan}: snapping one photo before boarding (Figure 1) fuses plate OCR with facial recognition because vehicles in Lahore are frequently shift-shared. From this real story, we mapped out all seven Data Science Lifecycle stages (Figure 2, Table 1).''
\end{speaking}

\subsection{B. Stage 1 --- Define: Turning Opinions into Testable Targets (Report Page 3)}
\begin{speaking}[Speaking Script: Define Stage]
\footnotesize
``In the \textbf{Define} stage, we recognized that `slow' and `overpriced' are purely subjective without context. A driver going 10 km/h in peak Mall Road gridlock is just stuck in traffic. We formulated two dimensionless ratios centered on \textbf{1.0 as normal}:
\begin{enumerate}\setlength{\itemsep}{0.8pt}\setlength{\parskip}{0pt}
  \item \textbf{Driving Pace Index (\(\Pi\)):} Driver speed divided by crowd-sourced median speed \(v_{\mathrm{base}}\) of peer rickshaws on that corridor and hour. \(\Pi < 0.75\) earns a \textbf{Habitually Slow} badge (Table 2).
  \item \textbf{Fare Fairness Ratio (\(\Phi\)):} Quoted fare divided by predicted fair fare (\(\approx 80\) PKR for 9.6 km; \(\approx 120\) PKR Raiwind to Gold Campus). \(\Phi > 1.25\) earns an \textbf{Overpriced} badge.''
\end{enumerate}
\end{speaking}

\subsection{C. Stage 2 --- Collect: Gathering Telemetry Responsibly (Report Page 3)}
\begin{speaking}[Speaking Script: Collect Stage]
\footnotesize
``In the \textbf{Collect} stage, since no public dataset links Lahore Qingqi drivers to GPS telemetry, we designed a 4-week pilot with 85 student volunteers commuting to \textbf{Superior University Gold Campus}. We simulated \textbf{1,224 rides}, \textbf{1,200 scans}, and \textbf{411,829 GPS pings} across \textbf{40 drivers} and 34 vehicles (Table 3, Figure 4).

We collect 5 streams: curbside photo (plate + face), quoted fare, 5-second GPS + accelerometer pings, corridor fare benchmarks, and shift registries. For privacy, raw photos are processed instantly on-device and discarded; only irreversible 128-dimensional mathematical embeddings are stored in our secure database.''
\end{speaking}

\newpage

\subsection{D. Stage 7 --- Deploy: Curbside Decision \& Operational Safeguards (Report Page 6)}
\begin{speaking}[Speaking Script: Deploy Stage]
\footnotesize
``In the \textbf{Deploy} stage (Figure 9), the passenger uses three clean screens: curbside scan, live ride telemetry, and an instant scorecard returned in \textbf{under two seconds} (alerting students when a 140 PKR quote exceeds the 80 PKR benchmark).

To protect driver livelihoods from false accusations, we engineered four operational safeguards (Table 6):
\begin{enumerate}\setlength{\itemsep}{0.8pt}\setlength{\parskip}{0pt}
  \item \textbf{The 5-Ride Rule:} Badges are suppressed until a driver logs \(\ge 5\) verified trips, absorbing single-trip traffic bad luck.
  \item \textbf{Shift-Shared Protection:} Profiles are indexed by composite \texttt{Plate\#FaceID}, so morning and night drivers sharing one vehicle have distinct records.
  \item \textbf{Recency Weighting \& Dispute Reviews:} Recent rides carry greater weight, and drivers can scan their own Qingqi to review scores and contest disputed trips.
  \item \textbf{Monthly Model Recalibration:} The fare regressor is updated monthly against official rolling petrol/LPG prices.''
\end{enumerate}
\end{speaking}

\section{Probable Teacher Questions \& Winning Answers}

\begin{qa}[Q1: Why do you need both number plate AND driver face? Isn't the plate enough?]
\footnotesize
\textbf{Answer:} In Lahore, Qingqi rickshaws are commonly rented out across morning and evening shifts. In our pilot, 6 out of 34 vehicles were shift-shared. If we tracked plates alone, an honest morning driver charging 80 PKR and an overpriced evening driver charging 140 PKR would be blended together. Facial recognition ensures each individual driver builds their own genuine reputation.
\end{qa}

\begin{qa}[Q2: What if a driver is delayed by an accident or police barricade? Do they get penalized?]
\footnotesize
\textbf{Answer:} No. First, the Pace Index \(\Pi\) normalizes speed against the ambient baseline \(v_{\mathrm{base}}\) of peer rickshaws on that road and hour (everyone slows down together). Second, badges require a \textbf{median across at least 5 verified rides}, meaning one unlucky delay has zero lasting effect on their rating.
\end{qa}

\begin{qa}[Q3: How does the student benefit in real life right at the roadside?]
\footnotesize
\textbf{Answer:} Within two seconds of snapping the photo, the student sees the fair benchmark range (75--85 PKR) and the driver's pace badge. If the driver demands 140 PKR, the student can either negotiate with confidence using the app's benchmark or politely hail the next Qingqi.
\end{qa}

\section{Saad's Key Numbers Cheat-Sheet}
\footnotesize
\begin{tabularx}{\textwidth}{|>{\bfseries\color{navyblue}}p{3.8cm}|X|>{\raggedleft\arraybackslash}p{3.0cm}|}
\hline
\rowcolor{navyblue}\textcolor{white}{\textbf{Metric}} & \textcolor{white}{\textbf{Context}} & \textcolor{white}{\textbf{Value to State}} \\ \hline
Campus \& Corridors & Superior University Gold Campus & 8 Routes, 85 Volunteers \\ \hline
Typical Qingqi Fares & Johar Town / Thokar to Gold Campus (9.6 km) & \textbf{80 PKR} (Fair benchmark) \\ \hline
Raiwind to Gold Campus & Longer morning commute corridor (16.1 km) & \textbf{120 PKR} (Fair benchmark) \\ \hline
Simulated Pilot Volume & 4 Weeks, 40 Drivers, 34 Qingqis & \textbf{1,224} Raw, \textbf{1,071} Clean \\ \hline
Curbside Latency & Time to return scorecard to student & \textbf{\(< 2\) Seconds} \\ \hline
Badge Minimum & Required verified trips before badge displays & \textbf{\(\ge 5\) verified rides} \\ \hline
\end{tabularx}

\end{document}
"""

KHUBAIB_TEX = COMMON_PREAMBLE.replace("__STUDENT_NAME__", "Muhammad Khubaib").replace("__ROLL_NO__", "SU92-BSCSM-F25-300") + r"""
% Top Banner
\begin{tcolorbox}[enhanced, colback=navyblue, colframe=navyblue, arc=3pt, left=8pt, right=8pt, top=4pt, bottom=4pt]
  {\fontsize{15pt}{17pt}\selectfont\color{white}\bfseries RahiScan \(\cdot\) Student Viva Study Guide}\\[1.5pt]
  {\fontsize{10pt}{12pt}\selectfont\color{softteal}\textbf{Member 2: Muhammad Khubaib} (Roll No: \texttt{SU92-BSCSM-F25-300})}\\[1pt]
  {\fontsize{8.5pt}{10.5pt}\selectfont\color{white!85!softblue}\textbf{Assigned Role:} Data Engineer \& Pipeline Analyst \(\cdot\) \textbf{Primary Stages:} Clean, Explore}
\end{tcolorbox}

\begin{overviewbox}[Quick 30-Second Group Overview (All Members Must Know This)]
\footnotesize
\begin{itemize}\setlength{\itemsep}{0.8pt}\setlength{\parskip}{0pt}
  \item \textbf{What is RahiScan?} A crowd-sourced mobile app proposal for students commuting by \textbf{Qingqi rickshaw} to \textbf{Superior University Gold Campus} (Raiwind Road) and across Lahore corridors.
  \item \textbf{The Core Problem:} Qingqi rickshaws lack fare meters. Curbside passengers face two unknowns: (1) Is the quoted fare fair or inflated? (2) Is the driver normal or habitually slow?
  \item \textbf{How It Works:} Snap one photo before boarding. The app reads the \textbf{number plate} and \textbf{driver's face}, checks past logs, and returns a scorecard in \textbf{\(< 2\) seconds}. During the trip, it logs 5-second GPS telemetry.
  \item \textbf{Status:} Comprehensive research proposal backed by a 4-week simulated pilot (\textbf{1,224 rides}, \textbf{40 drivers}).
\end{itemize}
\end{overviewbox}

\begin{tcolorbox}[enhanced, colback=white, colframe=bordergray, boxrule=0.4pt, arc=2.5pt, left=6pt, right=6pt, top=2.5pt, bottom=2.5pt]
  \footnotesize \textbf{Your Role in Simple Words:} You are the technical backbone of data quality. You explain how raw street telemetry was cleaned programmatically (\textbf{Clean}) --- specifically solving the walking-tail problem from our story --- and how you proved statistically that raw velocity is misleading while ambient normalization reveals true driver habits (\textbf{Explore}).
\end{tcolorbox}

\section{What to Say: Step-by-Step Viva Presentation Script}

\subsection{A. Stage 3 --- Clean: Resolving Street-Level Data Defects (Report Page 4)}
\begin{speaking}[Speaking Script: Clean Stage]
\footnotesize
``When collecting mobile sensor telemetry on chaotic urban roads, raw data cannot be trusted blindly. In our mock pilot, we addressed four concrete defects through our automated Python cleaning pipeline (Figure 5, left):
\begin{enumerate}\setlength{\itemsep}{0.8pt}\setlength{\parskip}{0pt}
  \item \textbf{Duplicate Uploads (\(1,224 \to 1,200\)):} Spotty cellular coverage causes phones to resend payloads. Deduplicated by user, corridor, and timestamp gap \(< 10\)s.
  \item \textbf{Fare Typos \& Missing Values (\(1,200 \to 1,151\)):} Commuters accidentally type extra zeroes (e.g., 800 instead of 80 PKR). Dropped records outside \([0.4, 4.0]\times\) corridor benchmark.
  \item \textbf{Plate OCR Glare \& Misreads (\(1,151 \to 1,090\)):} Glare and dirt degrade single-modality OCR. Requiring plate confidence \(\ge 0.85\) or face similarity \(\ge 0.70\) lifted driver verification precision from \textbf{83.5\% to 99.8\%}. Dropping 19 underpass GPS dropouts left \textbf{1,071 clean rides}.
  \item \textbf{The `Walking Tail' Trimmer (Figure 5, right):} Straight from our story! When a student rushes into class and forgets to hit `End Ride', the phone logs walking footsteps. This dragged average speed down by \(2.36\) km/h. Our backward filter identifies speed \(< 6\) km/h and accelerometer step variance \(> 1.0\,\mathrm{m/s^2}\) for \(\ge 60\)s, trimming \textbf{82.4\%} of all 148 walking tails with \textbf{100\% precision} (zero false trims).''
\end{enumerate}
\end{speaking}

\subsection{B. Stage 4 --- Explore: Uncovering Hidden Telemetry Patterns (Report Page 4)}
\begin{speaking}[Speaking Script: Explore Stage]
\footnotesize
``Once cleaned, exploratory data analysis proved why evaluating drivers by raw speed is fundamentally unfair:
\begin{itemize}\setlength{\itemsep}{0.8pt}\setlength{\parskip}{0pt}
  \item \textbf{The Traffic Heatmap (Figure 6, left):} On inner-city corridors like Mall Road, ambient median speed \(v_{\mathrm{base}}\) drops from 22 km/h at night to 10 km/h during evening rush hour, whereas Raiwind Road to Superior Gold Campus maintains higher speeds. Rush-hour drivers would be falsely penalized without normalization.
  \item \textbf{Ambient Normalization (\(\Pi\)):} Dividing observed speed by \(v_{\mathrm{base}}\) collapses drivers into traffic-invariant bands (Figure 6, right). Normal drivers stay in the shaded band across all congestion levels.
  \item \textbf{Bimodal Fare Distribution:} Plotting Fare Ratio \(\Phi\) reveals honest drivers cluster at 1.0 (\(\approx 80\) PKR for 9.6 km), while an overpriced group clusters around 1.7.
  \item \textbf{Table 4 Walkthrough:} Ride \texttt{TR-0467} (Raiwind to Gold Campus, 16.1 km) moved at 18.2 km/h (\(\Pi = 0.92\)) and charged 125 PKR (\(\Phi = 0.99\), Fair). Ride \texttt{TR-0427} on the same road crawled at 13.0 km/h (\(\Pi = 0.57\), Habitually Slow) and demanded 180 PKR (\(\Phi = 1.50\), Overpriced).''
\end{itemize}
\end{speaking}

\newpage

\section{Probable Teacher Questions \& Winning Answers}

\begin{qa}[Q1: How does your algorithm tell the difference between a rickshaw crawling in a traffic jam and a student walking to campus?]
\footnotesize
\textbf{Answer:} That is precisely why GPS speed alone fails! Both move at 4--5 km/h. We resolve this by fusing GPS speed with the phone's \textbf{accelerometer (inertial step sensor)}. An idling or crawling Qingqi produces smooth engine vibrations with low vertical acceleration variance (\(< 0.5\,\mathrm{m/s^2}\)), whereas human bipedal walking produces sharp, rhythmic heel-strike spikes (\(> 1.0\,\mathrm{m/s^2}\)). We only trim when slow speed AND high step variance coincide at the tail of a trip.
\end{qa}

\begin{qa}[Q2: What is \(v_{\mathrm{base}}\) and how is it calculated?]
\footnotesize
\textbf{Answer:} \(v_{\mathrm{base}}\) is the crowd-sourced ambient baseline speed. It is computed as the median observed speed of all clean rides logged on that specific corridor, within that two-hour time bucket, on that day type (weekday vs. weekend). It represents the `speed of the road' at that exact time.
\end{qa}

\begin{qa}[Q3: How many raw records did you start with and how many survived cleaning?]
\footnotesize
\textbf{Answer:} We began with \textbf{1,224 raw submissions}. 24 duplicates were removed (1,200), 49 typo/missing fares were dropped (1,151), 61 unverified scans were removed (1,090), and 19 low-coverage underpass trips were excluded, leaving \textbf{1,071 high-integrity rides} (an 87.5\% retention rate).
\end{qa}

\begin{qa}[Q4: Why not just use Mean speed instead of Median for the corridor baseline?]
\footnotesize
\textbf{Answer:} Vehicle speeds on urban Pakistani roads are skewed by occasional severe outliers (accidents, temporary roadblocks, VIP movements). The median is mathematically robust to outliers, ensuring our ambient baseline reflects the typical commuter experience rather than extreme anomalies.
\end{qa}

\section{Khubaib's Key Numbers Cheat-Sheet}
\footnotesize
\begin{tabularx}{\textwidth}{|>{\bfseries\color{navyblue}}p{3.8cm}|X|>{\raggedleft\arraybackslash}p{3.0cm}|}
\hline
\rowcolor{navyblue}\textcolor{white}{\textbf{Metric}} & \textcolor{white}{\textbf{Context}} & \textcolor{white}{\textbf{Value to State}} \\ \hline
Cleaning Funnel & Raw submissions to verified clean trips & \textbf{1,224 \(\to\) 1,071} (87.5\% kept) \\ \hline
Total GPS Pings & 5-second interval location and motion pings & \textbf{411,829} Pings \\ \hline
Biometric Fusion Gain & Plate OCR alone vs. Plate + Face fusion & \textbf{83.5\% \(\to\) 99.8\%} Precision \\ \hline
Walking Tail Filter & Recall across 148 forgotten `End Ride' walks & \textbf{82.4\%} Recall, \textbf{100\%} Precision \\ \hline
Speed Restoration & Velocity restored to drivers by trimming tails & \textbf{+2.36 km/h} median gain \\ \hline
Rush Hour Drop & Mall Road night speed vs. evening peak & \textbf{22 km/h \(\to\) 10 km/h} \\ \hline
\end{tabularx}

\end{document}
"""

HUZAIFA_TEX = COMMON_PREAMBLE.replace("__STUDENT_NAME__", "Huzaifa").replace("__ROLL_NO__", "SU92-BSCSM-F25-408") + r"""
% Top Banner
\begin{tcolorbox}[enhanced, colback=navyblue, colframe=navyblue, arc=3pt, left=8pt, right=8pt, top=4pt, bottom=4pt]
  {\fontsize{15pt}{17pt}\selectfont\color{white}\bfseries RahiScan \(\cdot\) Student Viva Study Guide}\\[1.5pt]
  {\fontsize{10pt}{12pt}\selectfont\color{softteal}\textbf{Member 3: Huzaifa} (Roll No: \texttt{SU92-BSCSM-F25-408})}\\[1pt]
  {\fontsize{8.5pt}{10.5pt}\selectfont\color{white!85!softblue}\textbf{Assigned Role:} Machine Learning \& Evaluation Lead \(\cdot\) \textbf{Primary Stages:} Model, Evaluate}
\end{tcolorbox}

\begin{overviewbox}[Quick 30-Second Group Overview (All Members Must Know This)]
\footnotesize
\begin{itemize}\setlength{\itemsep}{0.8pt}\setlength{\parskip}{0pt}
  \item \textbf{What is RahiScan?} A crowd-sourced mobile app proposal for students commuting by \textbf{Qingqi rickshaw} to \textbf{Superior University Gold Campus} (Raiwind Road) and across Lahore corridors.
  \item \textbf{The Core Problem:} Qingqi rickshaws lack fare meters. Curbside passengers face two unknowns: (1) Is the quoted fare fair or inflated? (2) Is the driver normal or habitually slow?
  \item \textbf{How It Works:} Snap one photo before boarding. The app reads the \textbf{number plate} and \textbf{driver's face}, checks past logs, and returns a scorecard in \textbf{\(< 2\) seconds}. During the trip, it logs 5-second GPS telemetry.
  \item \textbf{Status:} Comprehensive research proposal backed by a 4-week simulated pilot (\textbf{1,224 rides}, \textbf{40 drivers}).
\end{itemize}
\end{overviewbox}

\begin{tcolorbox}[enhanced, colback=white, colframe=bordergray, boxrule=0.4pt, arc=2.5pt, left=6pt, right=6pt, top=2.5pt, bottom=2.5pt]
  \footnotesize \textbf{Your Role in Simple Words:} You are the machine learning expert. You explain our two-tier AI architecture (\textbf{Model}) --- how computer vision identifies the driver and how Gradient Boosting predicts fair fares and classifies pace. Then, you lead the defense of our temporal holdout results (\textbf{Evaluate}), explaining the critical insight behind why single trips are noisy while multi-ride medians achieve 100\% accuracy.
\end{tcolorbox}

\section{What to Say: Step-by-Step Viva Presentation Script}

\subsection{A. Stage 5 --- Model: Two-Tier Machine Learning Pipeline (Report Page 5)}
\begin{speaking}[Speaking Script: Model Stage]
\footnotesize
``Our predictive architecture operates in two coordinated tiers (Figure 7, left):
\begin{enumerate}\setlength{\itemsep}{0.8pt}\setlength{\parskip}{0pt}
  \item \textbf{Tier 1 (Biometric \& OCR Identity Fusion):} Curbside images pass through a Convolutional Recurrent Neural Network (CRNN) to extract license text, while a MobileNetV3 backbone generates a compact 128-dimensional facial embedding. In our dataset, 6 vehicles are shared across shifts. For example, a single plate is driven by an honest morning driver (\(\Phi \approx 1.02\)) and an overpriced evening driver (\(\Phi \approx 1.75\)). Identity fusion resolves the true driver with \textbf{99.8\% precision}.
  \item \textbf{Tier 2 (Behavioural Prediction):} We train two Gradient Boosting models:
    \begin{itemize}\setlength{\itemsep}{0.6pt}\setlength{\parskip}{0pt}
      \item \textbf{Fair-Fare Regressor (GBR):} Predicts fair benchmark fare from distance, corridor ID, hour of day, weekend flag, and ambient speed \(v_{\mathrm{base}}\).
      \item \textbf{Pace Classifier (GBC):} Predicts whether driver pace is Slow, Normal, or Fast.
    \end{itemize}
  \item \textbf{The 4-Quadrant Driver Map (Figure 7, right):} Plotting 4-week driver medians confirms four distinct behavioral clusters. Most drivers sit in the `Fair \& Normal Pace' zone, 11 are `Overpriced', 3 are `Habitually Slow', and 2 drivers (\texttt{D27} and \texttt{D36}) are \textbf{both Slow AND Overpriced} --- exactly like our morning commute story!''
\end{enumerate}
\end{speaking}

\subsection{B. Stage 6 --- Evaluate: Temporal Holdout \& The `5-Ride Insight' (Report Page 5)}
\begin{speaking}[Speaking Script: Evaluate Stage]
\footnotesize
``To evaluate our models rigorously without data leakage, we trained strictly on \textbf{Weeks 1--3 (808 clean rides)} and evaluated on an unseen \textbf{Week-4 temporal holdout (263 rides across all 40 drivers)} (Table 5, Figure 8):
\begin{itemize}\setlength{\itemsep}{0.8pt}\setlength{\parskip}{0pt}
  \item \textbf{Fair-Fare Model Performance:} Our GBR achieved a holdout Mean Absolute Error (MAE) of \textbf{1.8 PKR}, easily beating our target of \(< 5\) PKR, beating distance-only linear regression (2.6 PKR), and heavily outperforming a flat median baseline (22.5 PKR).
  \item \textbf{Single-Ride Pace vs. Multi-Ride Medians (Table 5):} Single-trip pace reached macro \(F_1 = \mathbf{0.71}\), missing our aggressive \(0.88\) target (marked in red as `Not Met'). This was our most valuable engineering lesson! On a single trip, random street factors (a red light or temporary blockage) introduce noise.
  \item \textbf{The Solution (100\% Badge Accuracy):} When we aggregate a driver's trips over \textbf{\(\ge 5\) rides using the median}, single-trip noise cancels out completely, and driver Pace Badge accuracy reaches \textbf{100\%} (vs. only 90.0\% if raw speed were used). That empirical finding directly established our 5-ride safeguard in the Deploy stage.''
\end{itemize}
\end{speaking}

\newpage

\section{Probable Teacher Questions \& Winning Answers}

\begin{qa}[Q1: Why did you use a temporal holdout (Weeks 1--3 vs. Week 4) instead of standard 5-fold cross-validation?]
\footnotesize
\textbf{Answer:} Telemetry and fare data have a chronological time dimension. If you use random k-fold cross-validation, data points from Wednesday morning will be used to predict Tuesday afternoon, creating `temporal leakage' (cheating by using the future to predict the past). A temporal holdout mirrors real-world deployment: you train on past historical rides to predict future upcoming rides.
\end{qa}

\begin{qa}[Q2: In Table 5, Single-Ride Pace is marked `Not Met' (\(F_1 = 0.71\) vs. 0.88). Does that mean your pace model failed?]
\footnotesize
\textbf{Answer:} No, in fact it represents our most insightful data science finding! In an honest evaluation, catching model limitations is crucial. We proved that single rides are inherently stochastic (a fast driver can be trapped behind a stalled truck). However, by discovering this in the Evaluate stage, we engineered the solution: aggregating \(\ge 5\) rides via median lifts driver badge accuracy to \textbf{100\%}.
\end{qa}

\begin{qa}[Q3: Why choose Gradient Boosting over Deep Neural Networks or Linear Regression for fare prediction?]
\footnotesize
\textbf{Answer:} Tabular spatial-temporal features (distance, time bucket, categorical corridor, traffic index) have sharp non-linear interactions. Linear regression cannot capture congestion step-changes (MAE was 2.6 PKR vs 1.8 PKR for GBR). Deep neural networks require millions of parameters and are prone to overfitting on small tabular datasets, whereas Gradient Boosted Trees excel at tabular regression with fast, sub-millisecond inference suitable for mobile backends.
\end{qa}

\begin{qa}[Q4: Which features were most important in predicting fair fares?]
\footnotesize
\textbf{Answer:} Feature importance analysis showed that route distance accounted for \(\approx 67\%\) of the model weight, corridor routing accounted for \(\approx 32\%\), and ambient speed \(v_{\mathrm{base}}\) and hour of day captured peak congestion surcharges.
\end{qa}

\section{Huzaifa's Key Numbers Cheat-Sheet}
\footnotesize
\begin{tabularx}{\textwidth}{|>{\bfseries\color{navyblue}}p{3.8cm}|X|>{\raggedleft\arraybackslash}p{3.0cm}|}
\hline
\rowcolor{navyblue}\textcolor{white}{\textbf{Metric}} & \textcolor{white}{\textbf{Context}} & \textcolor{white}{\textbf{Value to State}} \\ \hline
Training / Holdout Split & Weeks 1--3 Train vs. Week 4 Test & \textbf{808 Train \(\cdot\) 263 Test} \\ \hline
Fair-Fare Holdout MAE & Gradient Boosting Regressor error & \textbf{1.8 PKR} (Target \(< 5\) PKR) \\ \hline
Linear Baseline MAE & Distance-only linear benchmark & \textbf{2.6 PKR} \\ \hline
Flat Rate Baseline MAE & Naive median baseline benchmark & \textbf{22.5 PKR} \\ \hline
Single-Trip Pace \(F_1\) & Holdout macro \(F_1\) on individual rides & \textbf{0.71} (vs. 0.54 raw speed) \\ \hline
Driver Badge Accuracy & Aggregated over \(\ge 5\) verified trips & \textbf{100\%} (vs. 90.0\% raw speed) \\ \hline
Fare Badge Accuracy & Overpriced classification accuracy & \textbf{100\%} across 40 drivers \\ \hline
\end{tabularx}

\end{document}
"""

def compile_guide(tex_filename, pdf_filename, name):
    tex_path = OUT_DIR / tex_filename
    print(f"Compiling {name} ({tex_path})...")
    
    # Run tectonic
    cmd = [r"C:\Users\ZEKT-1\tools\tectonic\tectonic.exe", "-X", "compile", tex_filename]
    res = subprocess.run(cmd, cwd=str(OUT_DIR), capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error compiling {name}:", res.stderr)
        raise RuntimeError(f"Tectonic failed on {tex_filename}")
    
    gen_pdf = OUT_DIR / pdf_filename
    root_pdf = ROOT / pdf_filename
    shutil.copy2(str(gen_pdf), str(root_pdf))
    
    # Check page count
    doc = pymupdf.open(str(gen_pdf))
    page_count = len(doc)
    doc.close()
    print(f"SUCCESS: {pdf_filename} compiled successfully! ({page_count} pages)")
    return page_count

def main():
    (OUT_DIR / "Study_Guide_Saad_Hussain.tex").write_text(SAAD_TEX, encoding="utf-8")
    (OUT_DIR / "Study_Guide_Khubaib.tex").write_text(KHUBAIB_TEX, encoding="utf-8")
    (OUT_DIR / "Study_Guide_Huzaifa.tex").write_text(HUZAIFA_TEX, encoding="utf-8")
    
    c1 = compile_guide("Study_Guide_Saad_Hussain.tex", "Study_Guide_Saad_Hussain.pdf", "Saad Hussain")
    c2 = compile_guide("Study_Guide_Khubaib.tex", "Study_Guide_Khubaib.pdf", "Khubaib")
    c3 = compile_guide("Study_Guide_Huzaifa.tex", "Study_Guide_Huzaifa.pdf", "Huzaifa")
    
    print("\nSummary:")
    print(f"1. Study_Guide_Saad_Hussain.pdf: {c1} pages")
    print(f"2. Study_Guide_Khubaib.pdf:      {c2} pages")
    print(f"3. Study_Guide_Huzaifa.pdf:      {c3} pages")

if __name__ == "__main__":
    main()
