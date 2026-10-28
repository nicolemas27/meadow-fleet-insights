MEADOW DISTRIBUTION — FLEET INSIGHTS PROTOTYPE

A small customer-facing proof of concept for Meadow Distribution's fleet manager. 
Synthetic data, 5–16 October 2026, 8 diesel vehicles.

HOW TO RUN IT
-------------
Double-click `index.html`. It opens in any modern browser. 
It works completely offline (no internet required).

THE TWO FINDINGS
----------------
1. VEH03 (Van): Idle share jumped from ~13% to ~40% on 12 October. 
   Action: Ask the fleet team what operationally changed on that date.

2. VEH06 (Truck): Uses ~26% more fuel than its identical peer (VEH05) every day. 
   Action: Send for a mechanical check.

The other 6 vehicles are behaving normally.

FOLDER CONTENTS
---------------
  index.html       - The interactive dashboard (open this)
  fleet_eda.ipynb  - The analytical notebook (cleaning, math, and stats)
  data.js          - The data payload for the dashboard
  chart.umd.min.js - The charting library (allows offline use)
  data/            - The raw CSV files supplied

DATA QUALITY
------------
The raw data was messy. I cleaned it by deduplicating sensor retries, removing 
impossible readings (like negative distance), and excluding events that 
didn't match the trip schedule. No missing values were filled in or estimated.

LIMITATIONS
-----------
No GPS, fuel receipts, or maintenance records were provided. Driving events 
are signals for investigation, not proof of unsafe driving, and should not 
be used for employment decisions.