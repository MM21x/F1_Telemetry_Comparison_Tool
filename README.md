# AI Race Engineer

A Python project focused on analysing motorsport telemetry and turning it into useful race-engineer feedback.

The first version uses FastF1 to work with Formula 1 timing and telemetry data. The aim is to compare laps, identify where performance is gained or lost, and produce clear feedback based on the data.

The longer-term goal is to adapt the project for sim-racing telemetry and eventually support live data, strategy analysis, and optional voice feedback.

## Current Features

- Load Formula 1 session data using FastF1
- Analyse lap and telemetry data
- Compare speed, throttle, braking, and sector performance
- Identify areas where time is gained or lost
- Generate structured race-engineer feedback

## Planned Development

- Add a simple dashboard for viewing telemetry
- Support imported sim-racing telemetry files
- Add live telemetry input through UDP or shared memory
- Detect fuel, tyre, pace, and consistency trends
- Add strategy and stint analysis
- Explore voice-based race-engineer feedback

## Technologies

- Python
- FastF1
- pandas
- NumPy
- matplotlib
- Plotly

## Getting Started

Install the required packages:

```bash
pip install fastf1 pandas numpy matplotlib plotly
```

FastF1 may cache downloaded session data locally so that the same data does not need to be downloaded repeatedly.

## Project Status

This project is currently in early development. The initial focus is offline Formula 1 telemetry analysis before moving towards sim-racing and live data support.

## Why I Am Building It

I am interested in the connection between software, data, and motorsport. This project is a way to explore how telemetry can be used to understand driver and car performance while developing practical skills in Python, data analysis, and real-time systems.
