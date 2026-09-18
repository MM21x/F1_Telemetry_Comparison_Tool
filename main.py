import os #creates cache folder 
import fastf1 #library for f1 data

#Create and enable a local cache so session data is reused between runs
os.makedirs("cache", exist_ok=True)
fastf1.Cache.enable_cache("cache")

#Build session data for 2024 monaco quali
session = fastf1.get_session(2024, "Monaco", "Q")

#Download and prepare the session data so laps become available
session.load()

#select fastest lap time of the session
fastest_lap = session.laps.pick_fastest()

#select fastest quali lap for selected drivers
lec_lap = session.laps.pick_drivers("LEC").pick_fastest()
ver_lap = session.laps.pick_drivers("VER").pick_fastest()

#get telemetary for each lap
lec_tel = lec_lap.get_car_data().add_distance()
ver_tel = ver_lap.get_car_data().add_distance()

#print key info to test setup
print("Session loaded successfully")
print("Event:", session.event["EventName"])
print("Session:", session.name)
print()

print("Fastest driver:", fastest_lap["Driver"])
print("Lap number:", fastest_lap["LapNumber"])
print("Lap time:", fastest_lap["LapTime"])

print("Lec fastest lap:", lec_lap["LapTime"])
print("Ver fastest lap:", ver_lap["LapTime"])
print()

print("LEC telemetry sample:")
print(
    lec_tel[["Distance", "Speed", "Throttle", "Brake", "nGear"]]
    .head()
    .reset_index(names="Row")
    .to_string(index=False)
)
print()

print("VER telemetry sample:")
print(
    ver_tel[["Distance", "Speed", "Throttle", "Brake", "nGear"]]
    .head()
    .reset_index(names="Row")
    .to_string(index=False)
)
print()