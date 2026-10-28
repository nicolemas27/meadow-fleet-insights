# Meadow Distribution (Fleet Insights Prototype)

A small customer-facing proof of concept for Meadow Distribution's fleet manager. 
Synthetic data, 5–16 October 2026, 8 diesel vehicles.

## How to Run It

Double-click `index.html`. It opens in any modern browser. 
It works completely offline.

## The Two Findings

1. **VEH03 (Van):** Idle share jumped from ~13% to ~40% on 12 October. 
   Action: Ask the fleet team what operationally changed on that date.

2. **VEH06 (Truck):** Uses ~26% more fuel than its identical peer (VEH05) every day. 
   Action: Send for a mechanical check.

The other 6 vehicles are behaving normally.

## Folder Contents

- `index.html` — The interactive dashboard (open this)
- `fleet_eda.ipynb` — The analytical notebook (cleaning, math, and stats)
- `data.js` — The data payload for the dashboard
- `chart.umd.min.js` — The charting library (allows offline use)
- `data/` — The raw CSV files supplied

## Data Quality

The raw data was messy. I cleaned it by:
- Deduplicating sensor retries.
- Removing impossible readings (like negative distance or 350 kph speeds).
- Excluding events that didn't match the trip schedule.

No missing values were filled in or estimated.

## Limitations

- No GPS, fuel receipts, or maintenance records were provided.
- Driving events are signals for investigation, not proof of unsafe driving. 
- Do not use this data to make employment decisions about drivers.
