import csv
import os


class FlightLogger:


    def __init__(self, filename):

        os.makedirs(
            "logs",
            exist_ok=True
        )

        self.file = open(
            filename,
            "w",
            newline=""
        )

        self.writer = csv.writer(self.file)


        self.writer.writerow([
            "time",
            "lat",
            "lon",
            "alt",
            "heading",
            "glitch_x",
            "glitch_y",
            "event"
        ])


    def log(
        self,
        position,
        glitch_x,
        glitch_y,
        event=""
    ):

        self.writer.writerow([

            position["time"],
            position["lat"],
            position["lon"],
            position["alt"],
            position["heading"],
            glitch_x,
            glitch_y,
            event

        ])

        self.file.flush()



    def close(self):

        self.file.close()