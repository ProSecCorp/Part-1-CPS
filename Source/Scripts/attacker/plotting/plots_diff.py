import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from pathlib import Path


LEGEND_COLORS = [
    "tab:blue",
    "tab:green",
    "tab:orange",
    "tab:red",
    "tab:purple",
    "tab:brown",
    "tab:pink",
    "tab:gray",
    "tab:olive",
    "tab:cyan",
]


def load_file(filename):

    data = pd.read_csv(filename)
    if "time" in data.columns:
        data = data.sort_values(by="time", ascending=True).reset_index(drop=True)

    return data


def plot_file(filename, line_label, line_color, line_style, event_offset):

    data = load_file(filename)
    events = data.get("event", pd.Series(dtype=str)).fillna("")
    event_specs = [
        "ATTACK_START",
        "RESET",
        "GPS Glitch or Compass error",
        "EKF3 lane switch 0",
        "EKF3 primary changed:0",
        "EKF3 lane switch 1",
        "EKF3 primary changed:1",
        "Glitch cleared",
    ]


    plt.plot(
        data.lon,
        data.lat,
        label=line_label,
        color=line_color,
        linestyle=line_style
    )


    for index, event_name in enumerate(event_specs):

        event_points = data[events == event_name]

        if not event_points.empty:

            marker_color = LEGEND_COLORS[(event_offset + index) % len(LEGEND_COLORS)]

            plt.scatter(
                event_points.lon,
                event_points.lat,
                color=marker_color,
                s=80,
                label=f"{event_name}",
                zorder=3
            )


choice = input(
    "Scegli il confronto (1=small_glitch vs no_glitch, 2=big_glitch vs no_glitch): "
).strip()

if choice == "1":
    primary_file = "logs/constant_small_glitch.csv"
    primary_label = "small value gps spoofing"
    primary_color = LEGEND_COLORS[0]
    primary_style = "--"
    no_glitch_color = LEGEND_COLORS[1]
elif choice == "2":
    primary_file = "logs/constant_big_glitch.csv"
    primary_label = "big value gps spoofing"
    primary_color = LEGEND_COLORS[0]
    primary_style = "--"
    no_glitch_color = LEGEND_COLORS[1]
else:
    print("Scelta non valida: inserisci 1 oppure 2")
    raise SystemExit(1)

if not Path(primary_file).exists():
    print(f"File mancante: {primary_file}")
    raise SystemExit(1)

no_glitch_file = "logs/constant_no_glitch.csv"

plt.figure(figsize=(12, 8))

plot_file(primary_file, primary_label, primary_color, primary_style, 2)
plot_file(no_glitch_file, "not spoofed gps", no_glitch_color, "-", 10)


plt.xlabel("Longitude")
plt.ylabel("Latitude")

axis_formatter = ScalarFormatter(useOffset=False)
axis_formatter.set_scientific(False)
plt.gca().xaxis.set_major_formatter(axis_formatter)
plt.gca().yaxis.set_major_formatter(axis_formatter)
plt.gca().invert_xaxis()

plt.legend()

plt.grid()

plt.title(f"{primary_label} VS not spoofed gps")

plt.show()