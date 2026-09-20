"""Compare a selected driver's fastest lap against P1 using FastF1 telemetry."""

import csv
import os # creates cache folder
import warnings

import fastf1 # library for f1 data
import fastf1.plotting  # plot styling + team colours
import fastf1.utils
from matplotlib import pyplot as plt

from fastf1.exceptions import InvalidSessionError, NoLapDataError


# Create and enable a local cache so session data is reused between runs
os.makedirs("cache", exist_ok=True)
os.makedirs("output", exist_ok=True)
fastf1.Cache.enable_cache("cache")

fastf1.set_log_level("ERROR")

# Hide FastF1 delta_time deprecation warning
warnings.filterwarnings(
    "ignore",
    message=r".*utils\.delta_time.*",
    category=FutureWarning
)

# Set up FastF1 plotting style
fastf1.plotting.setup_mpl()


# Format lap time into normal F1 timing style
# Return the time as minutes:seconds.milliseconds
def format_lap_time(lap_time):
    total_seconds = lap_time.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60

    if minutes > 0:
        return f"{minutes}:{seconds:06.3f}"
    return f"{seconds:.3f}"


def run_comparison():
    # User input for F1 sessions
    while True:
        try:
            year = int(input("Enter season year (e.g. 2024): ").strip())
            break
        except ValueError:
            print("Please enter a valid year.")

    event_name = input("Enter event name or round number (e.g Monaco or 8): ").strip()

    valid_sessions = {"FP1", "FP2", "FP3", "Q", "SQ", "SS", "S", "R"}

    while True:
            session_code = input(
                "Please enter a session code (FP1, FP2, FP3, Q(ualifying), S(print), SQ(sprint qualifying), R(race)): ").strip().upper()

            if session_code in valid_sessions:
                break
    
            print(f"Invalid session code: {session_code}")

    if event_name.isdigit():
        event_name = int(event_name)

    try:
        session = fastf1.get_session(year, event_name, session_code)
    except ValueError as error:
        raise ValueError(f"Invalid event or round for {year}: {event_name}") from error

    # Download and prepare the session data so laps become available
    print("\nLoading session data, please wait...", flush=True)
    session.load()
    print("Session data loaded.\n")

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

    if p1_lap is None:
        raise ValueError("No valid fastest lap found for this session.")
    
    # Get P1 details
    p1_driver = p1_lap["Driver"]
    p1_lap_time = p1_lap["LapTime"]
    p1_lap_number = p1_lap["LapNumber"]
    p1_team = p1_lap["Team"]
    p1_is_accurate = p1_lap["IsAccurate"]
    p1_color = fastf1.plotting.get_team_color(p1_team, session=session)

    print(f"Loaded: {session.event['EventName']} {session.name}")
    print(f"{p1_label}: {p1_driver}")
    print(f"Lap time: {format_lap_time(p1_lap_time)}")
    print(f"Lap number: {p1_lap_number}")
    print(f"Team: {p1_team}")
    print(f"Accurate lap: {p1_is_accurate}")
    print()

    while True:
        compare_driver = input(
            "Enter a driver codename (3 letters) to compare against P1 (e.g HAM, ALO): ").strip().upper()

        # Stop if user chooses the p1 driver
        if compare_driver == p1_driver:
            print(f"{compare_driver} is P1, choose a different driver")
            continue

        # Get chosen driver's fastest lap
        compare_lap = session.laps.pick_drivers(compare_driver).pick_fastest()

        # Stop if code is invalid or if theres no valid lap
        if compare_lap is None:
            print(f"No valid lap found for driver code: {compare_driver}")
            continue

        break

    # Get comparison driver details
    compare_lap_time = compare_lap["LapTime"]
    compare_lap_number = compare_lap["LapNumber"]
    compare_team = compare_lap["Team"]
    compare_is_accurate = compare_lap["IsAccurate"]
    compare_color = fastf1.plotting.get_team_color(compare_team, session=session)

    event_slug = str(session.event["EventName"]).replace(" ", "_")
    file_base = f"{year}_{event_slug}_{session_code}_{p1_driver}_vs_{compare_driver}"

    lap_gap = compare_lap_time - p1_lap_time

    ref_tel = p1_lap.get_car_data().add_distance()
    compare_tel = compare_lap.get_car_data().add_distance()

    ref_tel = ref_tel.copy()
    compare_tel = compare_tel.copy()

    p1_top_speed = ref_tel["Speed"].max()
    compare_top_speed = compare_tel["Speed"].max()
    top_speed_delta = compare_top_speed - p1_top_speed

    ref_tel["DRS_Open"] = ref_tel["DRS"].apply(lambda x: 1 if x in [2, 3, 10, 12, 14] else 0)
    compare_tel["DRS_Open"] = compare_tel["DRS"].apply(lambda x: 1 if x in [2, 3, 10, 12, 14] else 0)

    p1_s1 = p1_lap["Sector1Time"]
    p1_s2 = p1_lap["Sector2Time"]
    p1_s3 = p1_lap["Sector3Time"]

    compare_s1 = compare_lap["Sector1Time"]
    compare_s2 = compare_lap["Sector2Time"]
    compare_s3 = compare_lap["Sector3Time"]

    sector_comparison_available = not any(
        value is None for value in [p1_s1, p1_s2, p1_s3, compare_s1, compare_s2, compare_s3]
    )

    if sector_comparison_available:
        s1_gap = compare_s1 - p1_s1
        s2_gap = compare_s2 - p1_s2
        s3_gap = compare_s3 - p1_s3

        sector_gaps = {
            "Sector 1": s1_gap.total_seconds(),
            "Sector 2": s2_gap.total_seconds(),
            "Sector 3": s3_gap.total_seconds()
        }

        worst_sector = max(sector_gaps, key=sector_gaps.get)

    print(f"{compare_driver}:")
    print(f"Lap time: {format_lap_time(compare_lap_time)}")
    print(f"Lap number: {compare_lap_number}")
    print(f"Team: {compare_team}")
    print(f"Accurate lap: {compare_is_accurate}")
    print(f"Gap to P1: +{lap_gap.total_seconds():.3f}s")

    if sector_comparison_available:
        print(f"Sector 1 gap: {s1_gap.total_seconds():+.3f}s")
        print(f"Sector 2 gap: {s2_gap.total_seconds():+.3f}s")
        print(f"Sector 3 gap: {s3_gap.total_seconds():+.3f}s")
        print(f"Biggest loss: {worst_sector}")
    else:
        print("Sector comparison unavailable because one or more sector times are missing.")

    print()

    if sector_comparison_available:
        best_sector = min(sector_gaps, key=sector_gaps.get)

        if sector_gaps[best_sector] < 0:
            sector_recovery_text = f"{compare_driver} regained time in {best_sector}."
        else:
            sector_recovery_text = f"{compare_driver} did not gain time in any sector."

        speed_text = (
            f"Top speed deficit was {abs(top_speed_delta):.1f} km/h."
            if top_speed_delta < 0
            else f"Top speed advantage was {top_speed_delta:.1f} km/h."
            if top_speed_delta > 0
            else "Top speed was equal."
        )

        insight_text = (
            f"Insight: {compare_driver} lost most time in {worst_sector}. "
            f"{sector_recovery_text} {speed_text} "
            f"Brake, throttle, RPM, gear, and DRS traces were exported for visual comparison."
        )
    else:
        speed_text = (
            f"Top speed deficit was {abs(top_speed_delta):.1f} km/h."
            if top_speed_delta < 0
            else f"Top speed advantage was {top_speed_delta:.1f} km/h."
            if top_speed_delta > 0
            else "Top speed was equal."
        )

        insight_text = (
            f"Insight: Sector-level comparison was unavailable. {speed_text} "
            f"Brake, throttle, RPM, gear, and DRS traces were exported for visual comparison."
        )

    print(insight_text)

    csv_path = os.path.join("output", f"{file_base}_summary.csv")

    summary_row = {
        "year": year,
        "event": session.event["EventName"],
        "session": session_code,
        "reference_driver": p1_driver,
        "reference_team": p1_team,
        "reference_lap_time": format_lap_time(p1_lap_time),
        "reference_lap_number": p1_lap_number,
        "reference_top_speed_kmh": round(p1_top_speed, 1),
        "compare_driver": compare_driver,
        "compare_team": compare_team,
        "compare_lap_time": format_lap_time(compare_lap_time),
        "compare_lap_number": compare_lap_number,
        "compare_top_speed_kmh": round(compare_top_speed, 1),
        "gap_to_p1_s": round(lap_gap.total_seconds(), 3),
        "sector_1_gap_s": round(s1_gap.total_seconds(), 3) if sector_comparison_available else "",
        "sector_2_gap_s": round(s2_gap.total_seconds(), 3) if sector_comparison_available else "",
        "sector_3_gap_s": round(s3_gap.total_seconds(), 3) if sector_comparison_available else "",
        "biggest_loss": worst_sector if sector_comparison_available else "N/A",
        "top_speed_delta_kmh": round(top_speed_delta, 1),
        "insight": insight_text
    }

    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=summary_row.keys())
        writer.writeheader()
        writer.writerow(summary_row)

    print(f"Summary saved to: {csv_path}")
    print()

    # Plotting speed, throttle, and brake traces
    fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, 1, figsize=(12, 15), sharex=True)

    # Speed
    ax1.plot(ref_tel["Distance"], ref_tel["Speed"], color=p1_color, label=p1_driver)
    ax1.plot(compare_tel["Distance"], compare_tel["Speed"], color=compare_color, label=compare_driver)
    ax1.set_ylabel("Speed (km/h)")
    ax1.legend(loc="best")

    # Throttle
    ax2.plot(ref_tel["Distance"], ref_tel["Throttle"], color=p1_color, label=p1_driver)
    ax2.plot(compare_tel["Distance"], compare_tel["Throttle"], color=compare_color, label=compare_driver)
    ax2.set_ylabel("Throttle (%)")

    # Brake
    ax3.plot(ref_tel["Distance"], ref_tel["Brake"].astype(int) * 100, color=p1_color, label=p1_driver)
    ax3.plot(compare_tel["Distance"], compare_tel["Brake"].astype(int) * 100, color=compare_color, label=compare_driver)
    ax3.set_ylabel("Brake (%)")

    # RPM
    ax4.plot(ref_tel["Distance"], ref_tel["RPM"], color=p1_color, label=p1_driver)
    ax4.plot(compare_tel["Distance"], compare_tel["RPM"], color=compare_color, label=compare_driver)
    ax4.set_ylabel("RPM")

    # Gear
    ax5.step(ref_tel["Distance"], ref_tel["nGear"], where="post", color=p1_color, label=p1_driver)
    ax5.step(compare_tel["Distance"], compare_tel["nGear"], where="post", color=compare_color, label=compare_driver)
    ax5.set_ylabel("Gear")
    ax5.set_yticks(range(1, 9))

    # DRS
    ax6.step(ref_tel["Distance"], ref_tel["DRS_Open"], where="post", color=p1_color, label=p1_driver)
    ax6.step(compare_tel["Distance"], compare_tel["DRS_Open"], where="post", color=compare_color, label=compare_driver)
    ax6.set_ylabel("DRS")
    ax6.set_yticks([0, 1])
    ax6.set_yticklabels(["Off", "On"])
    ax6.set_xlabel("Distance (m)")
    fig.suptitle(
        f"{session.event['EventName']} {session.event.year} {session.name}\n"
        f"{p1_driver} vs {compare_driver} Telemetry Comparison",
        fontsize=14
    )

    plt.tight_layout(rect=[0, 0, 1, 0.97])

    plot_path = os.path.join("output", f"{file_base}_plot.png")
    fig.savefig(plot_path, dpi=300, bbox_inches="tight")
    print(f"Plot saved to: {plot_path}")

    plt.show()

def main():
    while True:
        try:
            run_comparison()
        except ValueError as error:
            print(f"\nError: {error}")
        except (InvalidSessionError, NoLapDataError) as error:
            print(f"\nFastF1 error: {error}")

        while True:
            again = input("\nRun another comparison? (Y/N): ").strip().upper()
            if again in {"Y", "N"}:
                break
            print("Please enter Y or N.")

        if again != "Y":
            print("Goodbye.")
            break


if __name__ == "__main__":
    main()