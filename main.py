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

#print key info to test setup
print("Session loaded successfully")
print("Event:", session.event["EventName"])
print("Session:", session.name)
print("Fastest driver:", fastest_lap["Driver"])
print("Lap number:", fastest_lap["LapNumber"])
print("Lap time:", fastest_lap["LapTime"])