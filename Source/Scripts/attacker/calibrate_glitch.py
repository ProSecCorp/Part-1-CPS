import time
import csv

from controller.glitch_controller import GlitchController
from gps_reader.gps_reader import GPSReader

glitch = GlitchController()
gps = GPSReader()

VALUES = [
    #0.0,
    0.000005,
    0.000010,
    0.000015,
    0.000020,
    0.000025,
    0.000030,
]

with open("logs/glitch_calibration.csv", "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "glitch_x",
        "glitch_y",
        "lat",
        "lon"
    ])

    print("Inizio calibrazione...\n")

    for value in VALUES:

        print(f"Imposto Y = {value}")

        glitch.set_glitch(0.0, value)

        time.sleep(3)

        pos = gps.get_raw_gps()

        print(
            pos["lat"],
            pos["lon"]
        )

        writer.writerow([
            0.0,
            value,
            pos["lat"],
            pos["lon"]
        ])

    glitch.reset()

print("\nFine.")