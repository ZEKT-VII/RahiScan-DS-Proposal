# RahiScan — Student Viva & Presentation Study Guide

> [!TIP]
> **How to use this guide:** Each member has their own section below matching Page 1 of the report. Read your **"What to Say"** script out loud twice — it uses simple, everyday language with zero heavy jargon, while still hitting every point the teacher will grade on.

---

## Quick 30-Second Group Overview (Everyone Should Know This)

- **What is our project?** We designed **RahiScan**, a mobile app proposal for students commuting by **Qingqi rickshaw** to **Superior University Gold Campus** (on Raiwind Road) and across inner-city Lahore.
- **What problem does it solve?** Lahore's Qingqi motorcycle-rickshaws don't have fare meters. When you stand at the curb, you face two mysteries:
  1. Is the driver asking for a fair price (like the standard **80 PKR** for a **9.6 km** ride, or **120 PKR** from **Raiwind to Superior University Gold Campus**) or overcharging me?
  2. Does this driver move at a normal speed, or do they crawl along the roadside and waste time even when the road is clear?
- **How does RahiScan work?** Before getting in, you take one photo of the Qingqi rickshaw. The app reads the **number plate** and checks the **driver's face**, looks up that driver's past rides, and in **2 seconds** shows you a scorecard: their **Speed Badge** (Slow / Normal / Fast) and the **Fair Price Range** in rupees. Once you sit inside, the app records GPS every 5 seconds to update that driver's record for future passengers.
- **Did we already launch it across Lahore?** No — this report is a **proposal** ("how we will build it"), tested on a **4-week simulated pilot (mock data)** of **1,224 Qingqi rides** and **40 drivers** to prove our pipeline works before real-world rollout.

---

# Part 1: Muhammad Saad Hussain (`SU92-BSCSM-F25-260`)
**Your Stages:** The Case Study Story + **Stage 1: Define** + **Stage 2: Collect** + **Stage 7: Deploy**  
*(Pages 1, 2, 3, and 6 of the Report)*

## 1. Your Role in Simple Words
You are the **Architect & Product Lead**. You start the presentation by telling the story of how we got the idea on our way to **Superior University Gold Campus**, how we turned our frustration into two simple scores (**Define**), what data the app needs to collect (**Collect**), and you finish the presentation by explaining how students will actually use the app safely in real life (**Deploy**).

## 2. What to Say (Step-by-Step Speaking Script)

### A. The Case Study Story & Lifecycle Extraction (Page 2)
> *"Our project started from a real Monday morning problem at 7:40 AM in Johar Town. We had an 8:30 AM lab at **Superior University Gold Campus** on Raiwind Road (about 9.6 km away). The first **Qingqi rickshaw** driver asked for **140 rupees**; we bargained it down to **110** and got on. Then he crawled along the left lane and even stopped for tea at a roadside dhaba, making us 12 minutes late. The very next morning, another Qingqi driver took us on the exact same 9.6 km route to Superior Gold Campus for the standard **80 rupees** in 20 minutes, even though traffic was heavier (similarly, from **Raiwind to Superior Gold Campus** is about **120 rupees**, and inner-city Lahore routes cost around **40 to 85 rupees**).*
>
> *From the roadside, both Qingqi rickshaws looked identical. So we proposed **RahiScan**: an app where a student snaps a photo of the Qingqi before boarding. As shown in **Figure 1**, the app reads the number plate and the driver's face. We check both because in Lahore, one Qingqi is often rented by two different drivers on day and night shifts. From this single morning story, we extracted all seven stages of the Data Science Lifecycle (**Figure 2** and **Table 1**)."*

### B. Stage 1 — Define: Turning Opinions into Numbers (Page 3, Top)
> *"In the **Define** stage, our problem was that saying 'this driver is slow' or 'he overcharged me' is just an opinion. A driver going 10 km/h during rush hour on Mall Road isn't slow — he's just stuck in traffic. So we defined two simple ratios where **1.0 means normal**:*
>
> 1. ***Driving Pace Index ($\Pi$):*** *We divide the driver's speed by the average speed of other Qingqi rickshaws on that same road at that same hour. If a driver scores **0.60**, it means they drove **40% slower** than the traffic around them. Under **0.75** gets a **Habitually Slow** badge (**Table 2**).*
> 2. ***Fare Fairness Ratio ($\Phi$):*** *We divide the price the driver asked for by the fair price for that trip (around **80 PKR** for 9.6 km, or **120 PKR** from Raiwind to Gold Campus). If a driver asks for 120 rupees on an 80-rupee route, their ratio is **1.50**. Anything consistently above **1.25** gets an **Overpriced** badge."*

### C. Stage 2 — Collect: What Data We Gather (Page 3, Bottom)
> *"In the **Collect** stage, since no public dataset exists for Lahore Qingqi drivers, we planned a 4-week pilot with 85 student volunteers commuting to **Superior University Gold Campus** (from Raiwind, Johar Town, Thokar Niaz Baig, and Township) and across inner-city Lahore routes. To test our code for this proposal, we generated a realistic mock dataset of **1,224 rides**, **1,200 photos**, and **411,829 GPS points** across **40 drivers** (**Table 3**).*
>
> *As shown in **Figure 4**, we collect five things: the curb photo (plate + face), the quoted fare in rupees, a GPS + motion sensor reading every 5 seconds during the ride, a reference corridor fare benchmark, and a driver shift list. For privacy, we immediately delete the driver's actual photo and only keep a 128-number code (embedding) so nobody can reconstruct their face."*

### D. Stage 7 — Deploy: Putting It in Students' Hands (Page 6)
> *"Finally, in the **Deploy** stage (**Figure 9**), the passenger uses just three screens: scan the Qingqi rickshaw, ride with live GPS tracking along Raiwind Road, and view the scorecard in **under 2 seconds** (for example, seeing that 140 PKR quoted is way above the 80 PKR fair fare) so they can bargain or wave the Qingqi away.*
>
> *We also added four fairness safeguards (**Table 6**):*
> 1. ***The 5-Ride Rule:*** *We never judge a driver from one bad trip. Until a driver has at least **5 verified rides**, the app simply says 'Insufficient Rides'.*
> 2. ***Shared Qingqi Protection:*** *Scores are tied to **Plate + Face** together, so a fair morning driver isn't punished for an overpriced evening driver sharing the same vehicle.*
> 3. ***Fresh Second Chances:*** *Recent rides count more than old rides, and drivers can scan their own plate to appeal a bad log.*
> 4. ***Monthly Fuel Updates:*** *Since petrol prices change in Pakistan, the fair-fare model retrains every month."*

## 3. Probable Teacher Questions for Saad
- **Q: Why do you need both the number plate AND the driver's face? Isn't the number plate enough?**  
  **A:** In Lahore, many Qingqi owners rent the same vehicle to two different drivers — one for the morning shift and one for the evening shift. In our data, 6 out of 34 Qingqis are shared like this. If we only used the number plate, a fair morning driver and an overpriced evening driver would get mixed into one fake average.
- **Q: What if a driver is recorded as slow just because there was an accident or VIP movement on the road?**  
  **A:** Two things protect them: first, we compare their speed to other Qingqis on that same road in that same hour ($\Pi$). Second, a driver only gets a badge based on their **median over at least 5 rides**, so one unlucky day never ruins their profile.

---

# Part 2: Muhammad Khubaib (`SU92-BSCSM-F25-300`)
**Your Stages:** **Stage 3: Clean** + **Stage 4: Explore**  
*(Page 4 of the Report)*

## 1. Your Role in Simple Words
You are the **Data Engineer & Analyst**. Real-world phone data from busy Lahore streets is full of mistakes. Your job is to explain how we cleaned out the bad data — especially the "walking tail" problem from our story (**Clean**) — and what patterns we discovered when we looked at the cleaned numbers (**Explore**).

## 2. What to Say (Step-by-Step Speaking Script)

### A. Stage 3 — Clean: Fixing Street-Level Data Mistakes (Page 4, Top)
> *"When students collect data on busy streets, four things go wrong, so we built four automatic cleaning rules (**Figure 5, left**):*
>
> 1. ***Duplicate Uploads (1,224 $\rightarrow$ 1,200):*** *Weak 4G signal causes phones to send the same ride twice within a few seconds. We automatically drop duplicates.*
> 2. ***Typing Mistakes in Fares (1,200 $\rightarrow$ 1,151):*** *Sometimes a student leaves the fare blank or accidentally types an extra zero — like 800 rupees instead of 80. Any fare that is more than 4 times or less than 0.4 times normal is filtered out.*
> 3. ***Blurry Plates at Night (1,151 $\rightarrow$ 1,090):*** *Dented plates or headlight glare make plate reading fail. By combining the plate reader with the face match, our accuracy in identifying the right driver jumped from **83.5% to 99.8%**. After also removing 19 rides where underpasses blocked GPS, we kept **1,071 clean rides**.*
> 4. ***The 'Walking Tail' Problem (Figure 5, right):*** *This comes straight from our story! When a student jumps out of the Qingqi late for lab at Superior Gold Campus and forgets to tap 'End Ride', the phone keeps recording their slow walk into the university building. That makes an honest driver look much slower! Our filter looks backward from the end of the trip: whenever speed drops below **6 km/h** AND the phone's motion sensor feels **walking footsteps** for over a minute, it chops off that walking tail. It caught **82.4%** of all 148 forgotten taps at **100% precision** and gave drivers back an average of **2.36 km/h**."*

### B. Stage 4 — Explore: Traffic vs. Driver Habit (Page 4, Bottom)
> *"Once the data was clean, we explored it to prove why raw speed is a terrible way to judge drivers.*
>
> *Look at **Figure 6 (left)** — our traffic heatmap. On inner-city routes like Mall Road, the normal speed of traffic is **22 km/h** at night, but drops to **10 km/h** during rush hour, whereas Raiwind Road to Superior Gold Campus moves faster.*
>
> *In **Figure 6 (right)**, when we plot each driver's speed against the traffic baseline, normal drivers fall neatly inside the shaded band, while truly slow drivers fall below it in red. And when we plot the Fare Ratio ($\Phi$), we see two clear groups: most Qingqi drivers cluster fairly around **1.0** (about **80 PKR** for a 9.6 km ride, or **120 PKR** from Raiwind to Superior Gold Campus), while an overpriced group clusters around **1.7**.*
>
> ***Table 4** shows real examples from our cleaned table: in Ride `TR-0794` from Johar Town to Gold Campus (10.0 km), the driver charged **80 PKR** (fair fare 79 PKR, $\Phi = 1.02$) and drove at normal speed ($\Pi = 1.02$). Meanwhile, on the Raiwind to Gold Campus route (16.1 km), fair driver `TR-0467` charged **125 PKR** ($\Phi = 0.99$), whereas slow & overpriced driver `TR-0427` crawled at 13 km/h ($\Pi = 0.57$) and demanded **180 PKR** ($\Phi = 1.50$)."*

## 3. Probable Teacher Questions for Khubaib
- **Q: How does the app know the difference between a Qingqi crawling in a traffic jam and a student walking to class?**  
  **A:** Both move under 6 km/h, which is why GPS speed alone isn't enough! We also check the phone's **accelerometer (step sensor)**. A Qingqi idling in traffic vibrates smoothly, whereas a student walking creates a rhythmic up-and-down footstep bounce (variance above $1.0\text{ m/s}^2$). We only cut the tail when **both** slow speed and walking steps happen together at the end of a ride.
- **Q: How many rides did you start with and how many survived cleaning?**  
  **A:** We started with **1,224 raw ride submissions** and ended with **1,071 clean, verified rides** (about 87.5% kept).

---

# Part 3: Huzaifa (`SU92-BSCSM-F25-408`)
**Your Stages:** **Stage 5: Model** + **Stage 6: Evaluate**  
*(Page 5 of the Report)*

## 1. Your Role in Simple Words
You are the **Machine Learning & Evaluation Lead**. Once Khubaib hands you the cleaned data, you explain how our AI models actually identify the driver and predict the fair Qingqi fare and pace (**Model**), and how we tested those models honestly on unseen Week-4 rides — including the one metric that missed its target and taught us our most important lesson (**Evaluate**).

## 2. What to Say (Step-by-Step Speaking Script)

### A. Stage 5 — Model: Two Tiers of AI (Page 5, Top)
> *"Our modelling stage (**Figure 7, left**) works in two steps:*
>
> *First is **Tier 1 (Identity Fusion)**: When a photo arrives, a lightweight plate reader (CRNN) reads the number plate and a face model (MobileNetV3) turns the driver's face into a 128-number signature. Combining them solves the shared-Qingqi problem. In our dataset, 6 Qingqis are shared between a fair morning driver ($\Phi \approx 1.02$) and an overpriced evening driver ($\Phi \approx 1.75$). Without face recognition, both would be merged into one wrong profile.*
>
> *Second is **Tier 2 (Behaviour Prediction)**: We use **Gradient Boosting** (a tree-based machine learning model that learns non-linear patterns) to predict the **Fair Qingqi Fare** from trip distance, corridor, time of day, weekend vs. weekday, and traffic speed. We also classify each driver's pace and pricing.*
>
> *When we plot all **40 drivers** after four weeks (**Figure 7, right**), they separate into four clear zones: most sit in the 'Fair & Normal Pace' zone, 11 sit in the 'Overpriced' zone, 3 are 'Habitually Slow', and 2 drivers (`LEP-2758` and `LES-8176`) are **both Slow AND Overpriced** — just like the driver from our Monday morning story!"*

### B. Stage 6 — Evaluate: Testing on Future Rides (Page 5, Bottom)
> *"To test our models honestly without cheating, we trained them only on **Weeks 1 to 3 (808 rides)** and tested them on **Week 4 (263 unseen rides)** (**Table 5** and **Figure 8**).*
>
> *First, our **Fair-Fare model** was off by an average of only **1.8 rupees** (MAE = 1.8 PKR), which easily beat our target of under 5 rupees, beat a simple straight-line distance formula (2.6 PKR), and crushed a flat median rate (22.5 PKR).*
>
> *Second — and this is our most interesting finding — look at the red 'Not Met' row in **Table 5**. When we tried to predict a driver's pace from a **single ride**, our $F_1$ score was **0.71** (our target was 0.88, and raw speed was only 0.54). Why did it miss 0.88? Because on any single trip, a slow driver might get lucky and hit every green traffic light, or a fast driver might get stuck behind a broken truck.*
>
> *However, when we take a driver's median across **5 or more rides**, that one-day luck cancels out, and our **Driver Badge accuracy jumps to 100%**! And as **Figure 8 (right)** shows, if we hadn't normalised for traffic speed, accuracy would have dropped to 90.0%. That evaluation result is the exact reason we created the 5-ride rule in the Deploy stage."*

## 3. Probable Teacher Questions for Huzaifa
- **Q: Why did you split the data into Weeks 1–3 for training and Week 4 for testing instead of a random 80/20 split?**  
  **A:** In real life, you train an app on past weeks and use it to predict future weeks. A random split would leak future traffic patterns into the past (temporal leakage). Testing on Week 4 proves the model works on future rides it has never seen.
- **Q: One of your targets in Table 5 says "Not Met" (Single-ride Pace = 0.71). Isn't that a failure?**  
  **A:** In data science, an honest evaluation is supposed to catch where a model is weak before you deploy it! Discovering that single-ride predictions are noisy ($0.71$) while 5-ride medians are $100\%$ accurate prevented us from unfairly labelling drivers after just one trip.

---

## Cheat-Sheet of Key Numbers (For All 3 Members)

| Fact | Number to Remember |
| :--- | :--- |
| **Target Vehicle & Campus** | **Qingqi Rickshaw** commuting to **Superior University Gold Campus** (Raiwind Rd) & inner-city Lahore |
| **Typical Fair Qingqi Fares** | **`~80 PKR`** for `9.6 km` (e.g. Johar Town to Gold Campus); **`~120 PKR`** from **Raiwind to Gold Campus** (`16.1 km`); **`40–85 PKR`** inner city |
| **Total Simulated Duration** | 4 Weeks (Weeks 1–3 Train = `808` rides; Week 4 Test = `263` rides) |
| **Total Drivers & Qingqis** | `40` drivers across `34` Qingqis (`6` shared between day/night shifts) |
| **Routes Covered** | `8` Lahore corridors (`85` student volunteers) |
| **Raw Rides vs. Clean Rides** | `1,224` raw submissions $\rightarrow$ `1,071` clean verified rides (`411,829` GPS pings) |
| **Driver ID Precision** | `99.8%` with Plate + Face fusion (vs. `83.5%` with Plate only) |
| **Walking-Tail Filter** | Caught `82.4%` of `148` forgotten *End Ride* walks at `100%` precision (`2.36 km/h` restored) |
| **Fair-Fare Prediction Error (MAE)** | **`1.8 PKR`** (Target was `< 5 PKR`; distance-only linear was `2.6 PKR`; flat rate was `22.5 PKR`) |
| **Pace Badge Accuracy** | `0.71` $F_1$ on 1 ride (*Not Met*) $\rightarrow$ **`100%` accuracy** across $\ge 5$ rides (*Met*) |
| **App Response Time** | Under `2 seconds` at the curb |
