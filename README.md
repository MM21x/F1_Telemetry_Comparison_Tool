# F1 Telemetry Comparison Tool

A Python project that compares a selected driver's fastest lap against the fastest lap in the same Formula 1 session using FastF1.

It prints lap and sector differences, generates a short performance summary, and saves a telemetry comparison chart and CSV summary. The project started as a motorsport data-analysis tool, but it is also intended as a foundation for a bigger idea: an AI race engineer for sim racing.

## What it does

- Loads an F1 session with FastF1
- Uses the fastest lap in the session as the reference lap
- Uses the fastest lap in Q3 as the reference for qualifying
- Lets you compare another driver's fastest lap against that reference
- Shows:
  - lap time gap
  - sector gaps
  - biggest time loss
  - top speed difference
- Generates an automatic insight summary
- Saves a CSV summary and telemetry plot for review

## Telemetry shown

The plot compares both drivers across:

- Speed
- Throttle
- Brake
- RPM
- Gear
- DRS

## Example output

Loaded: Miami Grand Prix Qualifying
Pole sitter: LEC
Lap time: 1:28.796

VER:
Lap time: 1:28.991
Gap to P1: +0.195s
Sector 1 gap: +0.105s
Sector 2 gap: +0.146s
Sector 3 gap: -0.056s
Biggest loss: Sector 2

Insight: VER lost most time in Sector 2. VER regained time in Sector 3. Top speed deficit was 3.4 km/h.
```

## Session codes

- FP1
- FP2
- FP3
- Q
- SQ
- SS
- S
- R

## Why I built it

I built this project to practise motorsport data analysis in Python and to explore how telemetry can be turned into something more useful than raw charts.

The bigger long-term idea is to use this as a base for an AI race engineer for sim racing: a tool that can compare laps, read telemetry, explain where time is being lost, and eventually give driver-focused feedback in a more useful and accessible way. Sim-racing telemetry platforms already use overlays, sector analysis, corner-by-corner comparisons, and automated feedback to help drivers improve, so this project is a first step toward that kind of system.

## Notes

- This project uses public FastF1 data, so it is not the same as real team-internal telemetry or engineering tools.
- Brake is shown as an on/off signal.
- DRS is simplified into open/closed for plotting.
- Results depend on the quality and availability of FastF1 session data.

## Tech used

- Python
- FastF1
- pandas
- Matplotlib
- CSV

## Future ideas

- Corner-by-corner brake analysis
- Braking point comparison
- Track map visualisation
- Animated replay of drivers around the circuit
- Comparing custom laps instead of only fastest laps
- AI-style driver feedback for sim racing