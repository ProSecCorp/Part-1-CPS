import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter


def plot_file(filename):

    data = pd.read_csv(filename)
    if "time" in data.columns:
        data = data.sort_values(by="time", ascending=True).reset_index(drop=True)

    events = data.get("event", pd.Series(dtype=str)).fillna("")
    event_specs = [
        ("ATTACK_START", "orange", "Attack start"),
        ("RESET", "red", "Reset"),
        ("AP: GPS Glitch or Compass error", "tab:purple", "GPS/Compass error"),
        ("AP: EKF3 lane switch 1", "tab:brown", "EKF3 lane switch"),
        ("AP: EKF3 primary changed:1", "tab:pink", "EKF3 primary changed"),
        ("AP: Glitch cleared", "tab:cyan", "Glitch cleared"),
    ]


    plt.figure(figsize=(12, 8))

    plt.plot(
        data.lon,
        data.lat,
        label="Drone"
    )


    plt.xlabel("Longitude")
    plt.ylabel("Latitude")

    axis_formatter = ScalarFormatter(useOffset=False)
    axis_formatter.set_scientific(False)
    plt.gca().xaxis.set_major_formatter(axis_formatter)
    plt.gca().yaxis.set_major_formatter(axis_formatter)
    plt.gca().invert_xaxis()

    for event_name, marker_color, marker_label in event_specs:

        event_points = data[events == event_name]

        if not event_points.empty:
            plt.scatter(
                event_points.lon,
                event_points.lat,
                color=marker_color,
                s=80,
                label=marker_label,
                zorder=3
            )

    plt.legend()

    plt.grid()

    plt.title(filename)

    plt.show()



choice = input("Choose the file to plot (1=constant_small, 2=constant_big, 3=adaptive): ").strip()

if choice == "1":
    plot_file("logs/constant_small_glitch.csv")
elif choice == "2":
    plot_file("logs/constant_big_glitch.csv")
elif choice == "3":
    plot_file("logs/adaptive_north_east_glitch.csv")
else:
    print("Invalid choice: please enter 1, 2 or 3")