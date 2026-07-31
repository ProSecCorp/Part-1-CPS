import csv
import re

input_file = "/home/darckat038/uni/cps/scripts/gps_raw_int_log.txt"
output_file = "/home/darckat038/uni/cps/scripts/gps_raw_int.csv"

# Regex per estrarre i campi dal formato GPS_RAW_INT
pattern = re.compile(
    r"time_usec\s*:\s*(\d+).*?"
    r"lat\s*:\s*(-?\d+).*?"
    r"lon\s*:\s*(-?\d+).*?"
    r"alt\s*:\s*(\d+).*?"
    r"vel\s*:\s*(\d+).*?"
    r"cog\s*:\s*(\d+)",
    re.DOTALL
)

rows = []

with open(input_file, "r") as f:
    for line in f:
        if "GPS_RAW_INT" not in line:
            continue

        match = pattern.search(line)
        if not match:
            continue

        time_usec = int(match.group(1))
        lat_degE7 = int(match.group(2))
        lon_degE7 = int(match.group(3))
        alt_mm = int(match.group(4))
        vel = int(match.group(5))
        cog = int(match.group(6))

        # Conversioni
        lat = lat_degE7 / 1e7
        lon = lon_degE7 / 1e7
        alt = alt_mm / 1000.0  # mm → m

        rows.append([time_usec, lat, lon, alt, vel, cog])

# Scrittura CSV
with open(output_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["time_usec", "lat", "lon", "alt_m", "vel_cm_s", "cog_deg"])
    writer.writerows(rows)

print("CSV generato:", output_file)
