
import sys
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# -----------------------------------------
# FOLDER SETTINGS
# -----------------------------------------

project_folder = Path(__file__).resolve().parent.parent
data_folder = project_folder / "Data"
graph_folder = project_folder / "Graphs"

graph_folder.mkdir(parents=True, exist_ok=True)

# Use CSV supplied by collector, or latest CSV
if len(sys.argv) > 1:
    filename = Path(sys.argv[1])
else:
    csv_files = list(
        data_folder.glob("ultrasonic_data*.csv")
    )

    if not csv_files:
        raise FileNotFoundError("No ultrasonic CSV files found!")

    filename = max(
        csv_files,
        key=lambda f: f.stat().st_mtime
    )

if not filename.is_file():
    raise FileNotFoundError(f"CSV file not found: {filename}")

print(f"\nReading file: {filename.name}")

# -----------------------------------------
# LOAD DATA
# -----------------------------------------

df = pd.read_csv(filename)

required_columns = [
    "actual_cm",
    "measured_cm",
    "reading_number"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"Missing CSV column: {column}")

for column in required_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

df = df.dropna(
    subset=["actual_cm", "reading_number"]
).copy()

if df.empty:
    raise ValueError("CSV contains no usable measurements.")

# Support multiple sessions in one CSV
if "session_id" not in df.columns:
    df["session_id"] = "session_1"

df["session_id"] = df["session_id"].fillna(
    "unknown_session"
).astype(str)

df["error_cm"] = (
    df["measured_cm"] - df["actual_cm"]
)

# Create experiment output folder
experiment_folder = graph_folder / filename.stem
experiment_folder.mkdir(parents=True, exist_ok=True)

# -----------------------------------------
# GENERATE GRAPHS
# -----------------------------------------

for session_id, session_data in df.groupby(
    "session_id", sort=False
):

    session_folder = experiment_folder / f"session_{session_id}"
    session_folder.mkdir(parents=True, exist_ok=True)

    print(f"\nSession: {session_id}")

    for distance in sorted(session_data["actual_cm"].unique()):

        distance_data = session_data[
            session_data["actual_cm"] == distance
        ].copy()

        distance_data = distance_data.sort_values(
            "reading_number"
        )

        readings = distance_data["measured_cm"]

        mean_value = readings.mean()
        std_value = readings.std()
        mean_error = mean_value - distance

        valid_count = readings.count()
        total_count = len(readings)

        print(f"\nActual Distance: {distance:g} cm")
        print(f"Mean Reading: {mean_value:.3f} cm")
        print(f"Standard Deviation: {std_value:.3f} cm")
        print(f"Mean Error: {mean_error:.3f} cm")
        print(f"Valid Readings: {valid_count}/{total_count}")

        # -------------------------------------
        # GRAPH 1: ACTUAL VS MEASURED
        # -------------------------------------

        plt.figure(figsize=(11, 6))

        plt.plot(
            distance_data["reading_number"],
            distance_data["measured_cm"],
            marker="o",
            markersize=3,
            linewidth=1,
            color="blue",
            label="Sensor Measurements"
        )

        plt.axhline(
            y=distance,
            color="green",
            linestyle="--",
            linewidth=2,
            label=f"Actual Distance ({distance:g} cm)"
        )

        if valid_count > 0:
            plt.axhline(
                y=mean_value,
                color="red",
                linewidth=2,
                label=f"Mean Reading ({mean_value:.2f} cm)"
            )

        plt.xlabel("Reading Number")
        plt.ylabel("Distance (cm)")

        plt.title(
            f"HC-SR04 Measurements at {distance:g} cm"
        )

        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        plt.savefig(
            session_folder /
            f"distance_{distance:g}cm_measurements.png",
            dpi=300
        )

        plt.close()

        # -------------------------------------
        # GRAPH 2: MEASUREMENT ERROR
        # -------------------------------------

        plt.figure(figsize=(11, 6))

        plt.plot(
            distance_data["reading_number"],
            distance_data["error_cm"],
            marker="o",
            markersize=3,
            linewidth=1,
            color="blue",
            label="Measurement Error"
        )

        plt.axhline(
            y=0,
            color="green",
            linestyle="--",
            linewidth=2,
            label="Zero Error"
        )

        if valid_count > 0:
            plt.axhline(
                y=mean_error,
                color="red",
                linewidth=2,
                label=f"Mean Error ({mean_error:.2f} cm)"
            )

        plt.xlabel("Reading Number")
        plt.ylabel("Error (cm)")

        plt.title(
            f"HC-SR04 Measurement Error at {distance:g} cm"
        )

        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        plt.savefig(
            session_folder /
            f"distance_{distance:g}cm_error.png",
            dpi=300
        )

        plt.close()

# -----------------------------------------
# SAVE STATISTICS
# -----------------------------------------

summary = df.groupby(
    ["session_id", "actual_cm"]
).agg(
    mean_measured=("measured_cm", "mean"),
    std_dev=("measured_cm", "std"),
    total_readings=("measured_cm", "size"),
    valid_readings=("measured_cm", "count")
).reset_index()

summary["mean_error"] = (
    summary["mean_measured"] - summary["actual_cm"]
)

summary["missing_readings"] = (
    summary["total_readings"] - summary["valid_readings"]
)

summary["missing_rate_percent"] = (
    summary["missing_readings"]
    / summary["total_readings"] * 100
)

summary.to_csv(
    experiment_folder / "sensor_statistics.csv",
    index=False
)

print("\nAll graphs generated successfully!")
print(f"Saved to: {experiment_folder}")
