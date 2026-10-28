# Meadow Distribution: Fleet Insights Prototype

A small proof of concept for Meadow Distribution's fleet manager. Synthetic data, 5 to 16 October 2026, 8 diesel vehicles.

## How to run it

Keep `index.html`, `data.js` and `chart.umd.min.js` in the same folder and open `index.html` in a browser. No internet connection is needed.

## The two findings

1. **VEH03 (van):** idle share rose from about 13% to about 40% from 12 October, across 9 different drivers.
   Action: ask the fleet team what changed on that date.

2. **VEH06 (rigid truck):** uses about 24% more fuel than its same-class peer VEH05 (26% above the class benchmark), on every day.
   Action: inspect VEH06 and compare it with VEH05. The cause could be mechanical, a fuel sensor fault or a depot difference (VEH06 runs from Depot South, VEH05 from Depot North).

The other six vehicles are within about 5% of their class benchmark.

## Rebuilding the data

Put the CSV files in a `data/` folder next to `build_data.py`, then run `python build_data.py` from that folder. It needs pandas and numpy and writes `data.js`.

## Running the notebook

Open `fleet_eda.ipynb` in Google Colab and upload the CSV files. The notebook reads them from `/content/`. To run it locally, change `DATA = '/content/'` to `DATA = 'data/'`. It needs pandas, numpy, matplotlib and scipy. Use Restart and Run All.

## Folder contents

- `index.html`: the dashboard (open this)
- `data.js`: the data for the dashboard, built by `build_data.py`
- `chart.umd.min.js`: the charting library, included so the dashboard works offline
- `build_data.py`: rebuilds `data.js` from the CSV files
- `fleet_eda.ipynb`: the analysis notebook (checks, cleaning, comparisons and statistical tests)
- `data/`: the CSV files supplied

## Data quality

The raw data needed cleaning:
- Repeated sensor rows were removed (24 telemetry rows and 12 events).
- Invalid readings (distance of 0 or less, and fuel that is blank or 10 L or more in one interval) are left out only of the calculations they affect.
- Six events were left out of event rates because their trip is unknown or their vehicle conflicts with the trip's vehicle.

No missing values were filled in or estimated.

## Limitations

- No GPS, fuel receipts or maintenance records were provided, so causes cannot be confirmed.
- Driving events are signals for investigation, not proof of unsafe driving. Do not use this data to make employment decisions about drivers.
- Benchmarks are illustrative, and the cost figures use a placeholder fuel price.
