# builds a csv of clean race laps to train the model on

import os
import traceback

import fastf1
import pandas as pd

os.makedirs("cache", exist_ok=True)
os.makedirs("output", exist_ok=True)
fastf1.Cache.enable_cache("cache")
races = [(year, rnd) for year in [2021, 2022] for rnd in range(1, 23)]
compounds = ["SOFT", "MEDIUM", "HARD"]

all_laps = []

for year, rnd in races:
    try:
        session = fastf1.get_session(year, rnd, "R")
        session.load(telemetry=False)

        laps = session.laps

        # remove pit laps, inaccurate laps and anything under a yellow/SC
        laps = laps[laps["PitInTime"].isna() & laps["PitOutTime"].isna()]
        laps = laps[laps["IsAccurate"] == True]
        laps = laps[laps["TrackStatus"] == "1"]
        laps = laps[laps["Compound"].isin(compounds)]
        laps = laps.dropna(subset=["LapTime", "TyreLife"])

        weather = laps.get_weather_data().reset_index(drop=True)
        laps = laps.reset_index(drop=True)

        data = pd.DataFrame()
        data["race"] = [f"{year}_{rnd:02d}"] * len(laps)
        data["driver"] = laps["Driver"]
        data["compound"] = laps["Compound"]
        data["tyre_life"] = laps["TyreLife"]
        data["lap_number"] = laps["LapNumber"]
        data["track_temp"] = weather["TrackTemp"]
        data["lap_time_s"] = laps["LapTime"].dt.total_seconds()

        # how much slower each lap is than the fastest clean lap in the race
        data["pace_delta_s"] = data["lap_time_s"] - data["lap_time_s"].min()

        all_laps.append(data)
        print(f"Loaded {year} round {rnd}")

    except Exception as error:
        print(f"Skipped {year} round {rnd}: {error}")
        
if len(all_laps) == 0:
    print("No rounds loaded, check the errors above")
    raise SystemExit

dataset = pd.concat(all_laps, ignore_index=True)
dataset.to_csv("output/laps_dataset.csv", index=False)
print(f"Saved {len(dataset)} laps from {dataset['race'].nunique()} races")