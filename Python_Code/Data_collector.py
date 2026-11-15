
import serial
import csv
import re
import subprocess

import sys
import argparse
from datetime import datetime
from pathlib import Path

# -----------------------------------------
# SETTINGS
# -----------------------------------------

parser = argparse.ArgumentParser(description="Collect Arduino ultrasonic measurements.")
parser.add_argument("--port", default="COM10", help="Arduino serial port (default: COM10)")
args = parser.parse_args()
PORT = args.port
BAUD_RATE = 9600
NUM_READINGS = 100

project_folder = Path(__file__).resolve().parent.parent
save_folder = project_folder / "Data"
graph_script = project_folder / "Python_Code" / "Graph_generator.py"

save_folder.mkdir(parents=True, exist_ok=True)

# Unique CSV filename
start_time = datetime.now()

filename = save_folder / (
    f"ultrasonic_data_{start_time.strftime('%Y-%m-%d_%H-%M-%S-%f')}.csv"
)

session_id = start_time.strftime("%Y%m%d_%H%M%S_%f")

current_distance = None
reading_count = 0
countdown = False
saved_readings = 0
exit_code = 0

arduino = None

try:
    # Open serial connection
    arduino = serial.Serial(PORT, BAUD_RATE, timeout=1)

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "session_id",
            "timestamp",
            "actual_cm",
            "reading_number",
            "measured_cm"
        ])

        file.flush()

        print("Connected to Arduino.")
        print(f"Saving data to: {filename}")
        print("Waiting for measurements...\n")

        while True:

            line = arduino.readline().decode(
                errors="replace"
            ).strip()

            if not line:
                continue

            # Control messages must remain reachable after a partial batch.
            if line in (
                "All measurements completed.",
                "Do you want to repeat the measurements? (y/n)",
            ):
                current_distance = None
                countdown = False

            # Detect target distance
            match = re.search(
                r"Measuring distance for Object at\s*(\d+)\s*cm",
                line
            )

            if match:
                current_distance = int(match.group(1))
                reading_count = 0
                countdown = True

                print(f"\nTarget distance: {current_distance} cm")
                continue

            # Ignore 10-second countdown
            if countdown:
                print("Countdown:", line)

                if line == "1":
                    countdown = False

                continue

            # Save sensor measurements
            if current_distance is not None and reading_count < NUM_READINGS:

                try:
                    measured = float(line)
                except ValueError:
                    continue

                reading_count += 1
                saved_readings += 1

                timestamp = datetime.now().isoformat(
                    timespec="milliseconds"
                )

                writer.writerow([
                    session_id,
                    timestamp,
                    current_distance,
                    reading_count,
                    measured
                ])
                file.flush()

                print(
                    f"{current_distance} cm | "
                    f"Reading {reading_count}/{NUM_READINGS}: "
                    f"{measured} cm"
                )

                if reading_count == NUM_READINGS:
                    file.flush()

                    print(
                        f"Completed {NUM_READINGS} readings "
                        f"at {current_distance} cm\n"
                    )

                    current_distance = None

                continue

            # Experiment completed
            if line == "All measurements completed.":
                print("\nAll measurements completed!")
                continue

            # Repeat experiment
            if line == "Do you want to repeat the measurements? (y/n)":

                answer = input(
                    "\nRepeat experiment? (y/n): "
                ).strip().lower()

                if answer not in ("y", "n"):
                    answer = "n"

                arduino.write(answer.encode())

                if answer == "n":
                    print("Experiment finished.")
                    break

                # New session ID for repeated experiment
                session_id = datetime.now().strftime(
                    "%Y%m%d_%H%M%S_%f"
                )

                continue

            print(line)

except KeyboardInterrupt:
    print("\nData collection interrupted.")

except serial.SerialException as error:
    print(f"\nArduino connection error: {error}")
    exit_code = 1

finally:
    if arduino is not None and arduino.is_open:
        arduino.close()

    if filename.is_file():
        print(f"\nData saved to: {filename}")

    # Automatically generate graphs
    if saved_readings > 0 and graph_script.is_file():

        print("\nGenerating graphs...")

        try:
            subprocess.run(
                [
                    sys.executable,
                    str(graph_script),
                    str(filename)
                ],
                check=True
            )

            print("\nGraphs generated successfully!")

        except subprocess.CalledProcessError as error:
            print(f"\nGraph generation failed: {error}")
            exit_code = 1

    elif saved_readings == 0:
        print("No measurements collected. Graphs not generated.")

    else:
        print(f"Graph generator not found: {graph_script}")
        exit_code = 1

sys.exit(exit_code)
