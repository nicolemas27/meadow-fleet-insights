# build_data.py: run once with  python build_data.py
import json
import numpy as np
import pandas as pd


def to_utc(s):
    return pd.to_datetime(s, format="ISO8601", utc=True).dt.round("s")


vehicles = pd.read_csv("data/vehicles.csv")
trips    = pd.read_csv("data/trips.csv")
samples  = pd.read_csv("data/telemetry_samples.csv")
events   = pd.read_csv("data/driver_events.csv")

trips["start_time_utc"]   = to_utc(trips["start_time_utc"])
trips["end_time_utc"]     = to_utc(trips["end_time_utc"])
samples["event_time_utc"] = to_utc(samples["event_time_utc"])
events["event_time_utc"]  = to_utc(events["event_time_utc"])
samples["date"] = samples["event_time_utc"].dt.strftime("%Y-%m-%d")

# --- cleaning (same as notebook section 3) ---
S = samples.drop_duplicates("sample_id").copy()
S["dist_ok"] = S["distance_km"] > 0
S["fuel_ok"] = S["fuel_used_l"].notna() & (S["fuel_used_l"] >= 0) & (S["fuel_used_l"] < 10)
S["pair_ok"] = S["dist_ok"] & S["fuel_ok"]
S = S.merge(trips[["trip_id", "vehicle_id", "driver_id", "route_type",
                   "load_band", "weather"]], on="trip_id")
S = S.merge(vehicles[["vehicle_id", "vehicle_class",
                      "illustrative_benchmark_l_per_100km"]], on="vehicle_id")
S = S.rename(columns={"illustrative_benchmark_l_per_100km": "bench"})
S["week"] = np.where(S["date"] < "2026-10-10", "week 1", "week 2")

# --- events cleaning (same as notebook section 2.7 / 6) ---
E = events.drop_duplicates("event_id").merge(
    trips[["trip_id", "vehicle_id", "route_type"]],
    on="trip_id", how="left", suffixes=("_event", ""))
E_ok = E[E["vehicle_id"] == E["vehicle_id_event"]].copy()


def agg(df, key):
    pairs = df[df["pair_ok"]]
    return pd.DataFrame({
        "km":     pairs.groupby(key, observed=True)["distance_km"].sum(),
        "L":      pairs.groupby(key, observed=True)["fuel_used_l"].sum(),
        "km_all": df[df["dist_ok"]].groupby(key, observed=True)["distance_km"].sum(),
        "idle":   df.groupby(key, observed=True)["idle_seconds"].sum(),
        "eng":    df.groupby(key, observed=True)["engine_on_seconds"].sum(),
        "trips":  df.groupby(key, observed=True)["trip_id"].nunique(),
    }).reset_index()


daily    = agg(S, ["vehicle_id", "date"])
weekly   = agg(S, ["vehicle_id", "week"])
v3_drv   = agg(S[S["vehicle_id"] == "VEH03"], ["driver_id", "week"])
v3_drv   = v3_drv[v3_drv["week"] == "week 2"]
rigid    = S[S["vehicle_id"].isin(["VEH05", "VEH06"])]
rigid_lb = agg(rigid, ["vehicle_id", "load_band"])

# --- rigid load-band wide, with gap column ---
rigid_lb["L100"] = 100 * rigid_lb["L"] / rigid_lb["km"]
rigid_wide = rigid_lb.pivot(index="load_band", columns="vehicle_id",
                            values="L100").reset_index()
rigid_wide["gap_pct"] = (rigid_wide["VEH06"] / rigid_wide["VEH05"] - 1) * 100
rigid_wide_records = rigid_wide.round(3).to_dict(orient="records")

# --- events: vehicle totals, per-type breakdown, per route ---
km_dist_vehicle = S[S["dist_ok"]].groupby("vehicle_id", observed=True)["distance_km"].sum()
km_dist_route   = S[S["dist_ok"]].groupby("route_type", observed=True)["distance_km"].sum()

ev_pivot = (E_ok.groupby(["vehicle_id", "event_type"], observed=True)
            .size().unstack(fill_value=0))
ev_pivot["total"] = ev_pivot.sum(axis=1)
ev_pivot = ev_pivot.reset_index()
ev_pivot["per_100km"] = (ev_pivot["total"] /
                         ev_pivot["vehicle_id"].map(km_dist_vehicle) * 100).round(2)
events_by_vehicle = ev_pivot.round(3).to_dict(orient="records")

ev_route = E_ok.groupby("route_type", observed=True).size().rename("events").reset_index()
ev_route["km"] = ev_route["route_type"].map(km_dist_route)
ev_route["per_100km"] = (ev_route["events"] / ev_route["km"] * 100).round(2)
events_by_route = ev_route.round(3).to_dict(orient="records")

ev_type = E_ok.groupby("event_type", observed=True).size().rename("events").reset_index()
events_by_type = ev_type.to_dict(orient="records")

# --- missing intervals  ---
unique_samples = samples.drop_duplicates("sample_id")
expected_observed = trips[["trip_id", "vehicle_id", "start_time_utc", "end_time_utc"]].copy()
expected_observed["expected"] = (
    (expected_observed["end_time_utc"] - expected_observed["start_time_utc"])
    .dt.total_seconds() / 300
).round().astype(int)
expected_observed["observed"] = (
    expected_observed["trip_id"].map(unique_samples.groupby("trip_id").size()).fillna(0).astype(int)
)
missing = expected_observed[expected_observed["observed"] < expected_observed["expected"]]
missing_intervals = [
    {"trip_id": r.trip_id, "vehicle_id": r.vehicle_id,
     "expected": int(r.expected), "observed": int(r.observed),
     "missing": int(r.expected - r.observed)}
    for r in missing.itertuples()
]

vehicle_route = (trips.groupby("vehicle_id")["route_type"]
                 .agg(lambda s: s.mode().iloc[0]).to_dict())

meta = {
    "dateMin":   str(daily["date"].min()),
    "dateMax":   str(daily["date"].max()),
    "vehicles":  vehicles.rename(columns={
        "illustrative_benchmark_l_per_100km": "bench"
    })[["vehicle_id", "vehicle_class", "depot", "bench"]].to_dict(orient="records"),
    "routes":    sorted(trips["route_type"].unique().tolist()),
    "classes":   sorted(vehicles["vehicle_class"].unique().tolist()),
    "vehicle_route": vehicle_route,
}

km_total = float(S[S["dist_ok"]]["distance_km"].sum())
km_valid = float(S[S["pair_ok"]]["distance_km"].sum())

dq = {
    "telemetry_raw":       int(len(samples)),
    "telemetry_clean":     int(len(S)),
    "duplicates_removed":  int(len(samples) - len(S)),
    "invalid_distance":    int((~S["dist_ok"]).sum()),
    "invalid_fuel":        int((~S["fuel_ok"]).sum()),
    "usable_l100":         int(S["pair_ok"].sum()),
    "km_total":            round(km_total, 1),
    "km_valid":            round(km_valid, 1),
    "km_pct_diff":         round(100 * (1 - km_valid / km_total), 2),
    "events_raw":          int(len(events)),
    "events_clean":        int(len(E)),
    "events_linked":       int(len(E_ok)),
    "events_excluded":     int(len(E) - len(E_ok)),
    "events_unknown_trip": int((E["trip_id"] == "TRP_UNKNOWN").sum()),
    "missing_intervals":   missing_intervals,
}

out = {
    "meta":                 meta,
    "daily":                daily.round(3).to_dict(orient="records"),
    "weekly":               weekly.round(3).to_dict(orient="records"),
    "v3_driver_week":       v3_drv.round(3).to_dict(orient="records"),
    "rigid_loadband_wide":  rigid_wide_records,
    "events_by_vehicle":    events_by_vehicle,
    "events_by_route":      events_by_route,
    "events_by_type":       events_by_type,
    "dq":                   dq,
}

with open("data.js", "w") as f:
    f.write("window.FLEET_DATA = ")
    json.dump(out, f, indent=2)
    f.write(";\n")

print(
    f"wrote data.js: {len(daily)} daily rows, {len(weekly)} weekly rows, "
    f"{len(events_by_vehicle)} vehicles with events, "
    f"{len(missing_intervals)} trips with missing intervals"
)