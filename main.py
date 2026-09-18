import os #creates cache folder 
import fastf1 #library for f1 data
import fastf1.plotting #plot styling + team colours
from matplotlib import pyplot as plt

#Create and enable a local cache so session data is reused between runs
os.makedirs("cache", exist_ok=True)
fastf1.Cache.enable_cache("cache")

#set up FastF1 plotting style
fastf1.plotting.setup_mpl()

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

# get team colours for the plot lines
lec_color = fastf1.plotting.get_team_color(lec_lap["Team"], session=session)
ver_color = fastf1.plotting.get_team_color(ver_lap["Team"], session=session)

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

#plotting both speed traces on the same graph
fig, ax = plt.subplots(figsize=(12,6))
ax.plot(lec_tel["Distance"], lec_tel["Speed"], color=lec_color, label="LEC")
ax.plot(ver_tel["Distance"], ver_tel["Speed"], color=ver_color, label="VER")

ax.set_title(f"{session.event['EventName']} {session.event.year} Qualifying\nFastest Lap Speed Comparison")
ax.set_xlabel("Distance (m)")
ax.set_ylabel("Speed (km/h)")
ax.legend()

plt.tight_layout()
plt.show()