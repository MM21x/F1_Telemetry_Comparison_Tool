"""Compare a selected driver's fastest lap against P1 using FastF1 telemetry."""

import os #creates cache folder

import fastf1 #library for f1 data
import fastf1.plotting #plot styling + team colours
import fastf1.utils
from matplotlib import pyplot as plt

#Create and enable a local cache so session data is reused between runs
os.makedirs("cache", exist_ok=True)
fastf1.Cache.enable_cache("cache")

fastf1.set_log_level("WARNING")

#set up FastF1 plotting style
fastf1.plotting.setup_mpl()

#user input for f1 sessions
year = int(input("Enter season year (e.g. 2024): ").strip())
#  .strip removes whitespace from start and end of string

event_name = input("Enter event name or round number (e.g Monaco or 8): ").strip()

session_code = input("Please enter a session code (FP1, FP2, FP3, Q(ualifying), S(print), SQ(sprint qualifying), R(race)): ").strip().upper()

valid_sessions = {"FP1", "FP2", "FP3", "Q", "SQ", "SS", "S", "R"}

if session_code not in valid_sessions:
    raise ValueError(f"Invalid session code: {session_code}")

if event_name.isdigit():
    event_name = int(event_name)

session = fastf1.get_session(year, event_name, session_code)

#Download and prepare the session data so laps become available
session.load()

# Use Q3 fastest lap as P1 in qualifying, otherwise use fastest lap in session
if session_code == "Q":
    _, _, q3 = session.laps.split_qualifying_sessions()

    # Stop if Q3 data is missing
    if q3 is None or q3.empty:
        raise ValueError("Q3 data is not available for this qualifying session.")

    p1_lap = q3.pick_fastest()
    p1_label = "Pole sitter"
else:
    p1_lap = session.laps.pick_fastest()
    p1_label = "Fastest lap in session"


# Get P1 driver, lap time and team colour
p1_driver = p1_lap["Driver"]
p1_lap_time = p1_lap["LapTime"]
p1_color = fastf1.plotting.get_team_color(p1_lap["Team"], session=session)

# Format lap time into normal F1 timing style
# Return the time as minutes:seconds.milliseconds
def format_lap_time(lap_time):
    total_seconds = lap_time.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60

    if minutes > 0:
        return f"{minutes}:{seconds:06.3f}"
    return f"{seconds:.3f}"


print()
print(f"Loaded: {session.event['EventName']} {session.name}")
print(f"{p1_label}: {p1_driver}")
print(f"Lap time: {format_lap_time(p1_lap_time)}")
print()

compare_driver = input("Enter a driver codename (3 letters) to compare against P1 (e.g HAM, ALO): ").strip().upper()

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

#plotting both speed traces on the same graph, delta time on second axis, leclerc as comparison lap
# plotting speed trace + delta time, P1 as reference lap
fig, ax1 = plt.subplots(figsize=(12, 6))

ax1.plot(ref_tel["Distance"], ref_tel["Speed"], color=p1_color, label=p1_driver)
ax1.plot(compare_tel["Distance"], compare_tel["Speed"], color=compare_color, label=compare_driver)
ax1.set_xlabel("Distance (m)")
ax1.set_ylabel("Speed (km/h)")

ax2 = ax1.twinx()
ax2.plot(ref_tel["Distance"], delta_time, color="white", linestyle="--", label=f"Delta to P1: ({p1_driver})")
ax2.set_ylabel("Delta time (s)")

ax1.set_title(f"{session.event['EventName']} {session.event.year} {session.name}\nSpeed Trace + Delta Time")

lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="best")

plt.tight_layout()
plt.show()
