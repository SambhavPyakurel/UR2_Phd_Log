# Ultrasonic sensor experiment

See the [Project Progress Log](PROGRESS_LOG.md) for weekly updates.

The Arduino collects 100 readings at each of 5, 10, 15, 20, 25, and 30 cm.
Move the target to the announced distance during each ten-second countdown.
Python saves the serial readings and generates measurement/error plots and statistics.

## Folder layout

- `ultrasonic_sensor_main/`: Arduino sketch; keep the folder and sketch names matched.
- `Python_Code/`: data collector and graph generator.
- `Data/`: raw measurement CSV files.
- `Graphs/`: generated plots and summary statistics, grouped by experiment and session.
- `.venv/`: local Python environment and dependencies.
- `.vscode/` and `.idea/`: editor settings.
- `requirements.txt`: Python dependency list.

## Setup and run (Windows PowerShell)

Install Python 3.10 or newer, then run from this project folder:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Upload `ultrasonic_sensor_main/ultrasonic_sensor_main.ino` using Arduino IDE
with the appropriate board selected. The sketch uses trigger pin 9 and echo
pin 10. Use sensor wiring and signal levels compatible with your board.

Find the Arduino port and start collecting:

```powershell
.\.venv\Scripts\python.exe -m serial.tools.list_ports
.\.venv\Scripts\python.exe Python_Code/Data_collector.py --port COM10
```

Replace COM10 with the actual Arduino port. Close Arduino Serial Monitor before
collecting. If the board does not restart when the serial connection opens,
press its reset button after the collector connects. Answer `y` to repeat or
`n` to finish and generate graphs. Ctrl+C also preserves collected readings
and attempts graph generation.

CSV files are saved in `Data`; plots and statistics are saved in `Graphs`.
Paths are relative to the scripts' project folder, not the terminal directory.
`NaN` readings represent echo timeouts and are counted as missing in statistics.

Regenerate graphs from the most recently modified CSV, or supply a specific CSV:

```powershell
.\.venv\Scripts\python.exe Python_Code/Graph_generator.py
.\.venv\Scripts\python.exe Python_Code/Graph_generator.py Data/your_file.csv
```

