import csv
import re
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# -----------------------------
# FILE DI INPUT
# -----------------------------
log_file = "/home/darckat038/uni/cps/scripts/gps_raw_int_log.txt"
csv_file = "/home/darckat038/uni/cps/scripts/gps_with_events.csv"

# -----------------------------
# 1. PARSING DEL LOG
# -----------------------------

gps_pattern = re.compile(
    r"time_usec\s*:\s*(\d+).*?"
    r"lat\s*:\s*(-?\d+).*?"
    r"lon\s*:\s*(-?\d+).*?"
    r"alt\s*:\s*(\d+)",
    re.DOTALL
)

records = []
pending_events = []


def parse_gps_row(line):
    match = gps_pattern.search(line)
    if not match:
        return None
    return [
        int(match.group(1)),
        int(match.group(2)) / 1e7,
        int(match.group(3)) / 1e7,
        int(match.group(4)) / 1000.0,
        "gps",
        "",
    ]


def parse_event_message(line):
    message = line.strip()
    if not message:
        return None
    if message.startswith("/*"):
        return None
    if "battery" in message.lower():
        return None
    if "GPS_RAW_INT" in message:
        return None
    if message.startswith("AP:"):
        message = message.removeprefix("AP:").strip()
    return message or None


def interpolate_value(start, end, factor):
    return start + (end - start) * factor


def is_ekf3_message(event_message):
    return "EKF3 lane switch" in event_message or "EKF3 primary changed" in event_message


def merge_pending_events(event_messages):
    merged_messages = []
    ekf3_messages = [message for message in event_messages if is_ekf3_message(message)]

    if ekf3_messages:
        deduplicated = []
        for message in ekf3_messages:
            if message not in deduplicated:
                deduplicated.append(message)
        merged_messages.append("EKF3 lane switch: " + " / ".join(deduplicated))

    for message in event_messages:
        if is_ekf3_message(message):
            continue
        merged_messages.append(message)

    return merged_messages


def event_style(event_message):
    if "GPS Glitch or Compass error" in event_message:
        return "red", "x", "GPS Glitch"
    if is_ekf3_message(event_message) or event_message.startswith("EKF3 lane switch:"):
        return "orange", "^", "EKF Lane Switch"
    if "Glitch cleared" in event_message:
        return "green", "o", "Glitch Cleared"
    return "blue", "D", event_message

with open(log_file, "r") as f:
    last_gps_row = None
    for line in f:
        gps_row = parse_gps_row(line)
        if gps_row is not None:
            if last_gps_row is None:
                records.append(gps_row)
            else:
                if pending_events:
                    merged_events = merge_pending_events(pending_events)
                    total_events = len(merged_events)
                    for index, event_message in enumerate(merged_events, start=1):
                        factor = index / (total_events + 1)
                        records.append([
                            int(round(interpolate_value(last_gps_row[0], gps_row[0], factor))),
                            interpolate_value(last_gps_row[1], gps_row[1], factor),
                            interpolate_value(last_gps_row[2], gps_row[2], factor),
                            interpolate_value(last_gps_row[3], gps_row[3], factor),
                            "event",
                            event_message,
                        ])
                    pending_events.clear()

                records.append(gps_row)

            last_gps_row = gps_row
            continue

        event_message = parse_event_message(line)
        if event_message is not None:
            pending_events.append(event_message)

if pending_events and last_gps_row is not None:
    for event_message in merge_pending_events(pending_events):
        records.append([
            last_gps_row[0],
            last_gps_row[1],
            last_gps_row[2],
            last_gps_row[3],
            "event",
            event_message,
        ])

# -----------------------------
# 3. SCRIVO IL CSV
# -----------------------------
with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["time_usec", "lat", "lon", "alt", "record_type", "event"])
    writer.writerows(records)

print("CSV generato:", csv_file)
print("Eventi inseriti:", sum(1 for row in records if row[4] == "event"))

# -----------------------------
# 4. PLOT LAT/LON CON MARKER EVENTI INTERPOLATI
# -----------------------------

gps_only = [row for row in records if row[4] == "gps"]

plt.figure(figsize=(10, 8))
plt.plot([row[1] for row in gps_only], [row[2] for row in gps_only], '-', color="black", linewidth=1.5)

for row in records:
    if row[4] != "event":
        continue

    color, marker, label = event_style(row[5])
    plt.scatter(row[1], row[2], color=color, s=80, marker=marker)  # type: ignore[arg-type]
    plt.text(row[1], row[2], label, color=color, fontsize=9)

ax = plt.gca()
ax.xaxis.set_major_formatter(ScalarFormatter(useOffset=False))
ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
ax.ticklabel_format(style="plain", axis="both", useOffset=False)

plt.xlabel("Latitudine")
plt.ylabel("Longitudine")
plt.title("Traiettoria GPS con Eventi interpolati")
plt.grid(True)
plt.tight_layout()
plt.show()
