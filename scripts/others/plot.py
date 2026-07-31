import csv
import matplotlib.pyplot as plt

csv_file = "/home/darckat038/uni/cps/scripts/gps_raw_int.csv"

lats = []
lons = []

with open(csv_file, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        lats.append(float(row["lat"]))
        lons.append(float(row["lon"]))

plt.figure(figsize=(10, 8))
plt.plot(lons, lats, '-', linewidth=1.5)

plt.xlabel("Longitudine")
plt.ylabel("Latitudine")
plt.title("Traiettoria GPS (solo lat/lon)")
plt.grid(True)
plt.tight_layout()
plt.show()
