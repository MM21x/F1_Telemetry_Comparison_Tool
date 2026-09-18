"""Compare a selected driver's fastest qualifying lap against P1 using FastF1 telemetry."""

import os #creates cache folder

import fastf1 #library for f1 data
import fastf1.plotting #plot styling + team colours
import fastf1.utils
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

# Calculate delta time using P1 (fastest qualifying lap) as the reference lap
p1_lap = session.laps.pick_fastest()
p1_driver = p1_lap["Driver"]
p1_color = fastf1.plotting.get_team_color(p1_lap["Team"], session=session)

compare_driver = input("Enter a driver codename (3 letters) to compare against The Fastest Lap (p1) (e.g HAM, ALO): ").strip().upper()

#get chosen drivers fastest lap
compare_lap = session.laps.pick_drivers(compare_driver).pick_fastest()

#stop if code is invalid or if theres no valid lap
if compare_lap is None:
    raise ValueError(f"No valid lap found for driver code: {compare_driver}")

#stop if user chooses the p1 driver
if compare_driver == p1_driver:
    raise ValueError(f"{compare_driver} is P1, choose a different driver")

compare_color = fastf1.plotting.get_team_color(compare_lap["Team"], session=session)

delta_time, ref_tel, compare_tel = fastf1.utils.delta_time(p1_lap, compare_lap)

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

#plotting both speed traces on the same graph, delta time on second axis, leclerc as comparison lap
# plotting speed trace + delta time, P1 as reference lap
fig, ax1 = plt.subplots(figsize=(12, 6))

ax1.plot(ref_tel["Distance"], ref_tel["Speed"], color=p1_color, label=p1_driver)
ax1.plot(compare_tel["Distance"], compare_tel["Speed"], color=compare_color, label=compare_driver)
ax1.set_xlabel("Distance (m)")
ax1.set_ylabel("Speed (km/h)")

ax2 = ax1.twinx()
ax2.plot(ref_tel["Distance"], delta_time, color="white", linestyle="--", label=f"Delta to P1:{p1_driver}")
ax2.set_ylabel("Delta time (s)")

ax1.set_title(f"{session.event['EventName']} {session.event.year} Qualifying\nSpeed Trace + Delta Time")

lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="best")

plt.tight_layout()
plt.show()
