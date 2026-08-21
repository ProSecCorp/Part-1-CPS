from utils.geo_utils import distance


class HijackPlanner:

    def __init__(
        self,
        target_lat,
        target_lon,
        step=2e-6,
        hold_radius=2,
    ):

        self.target_lat = target_lat
        self.target_lon = target_lon

        self.step = step

        self.hold_radius = hold_radius

        self.glitch_x = 0
        self.glitch_y = 0

        self.state = "APPROACH"

    def update(
        self,
        real_lat,
        real_lon,
    ):

        spoof_lat = real_lat + self.glitch_x
        spoof_lon = real_lon + self.glitch_y

        error = distance(
            spoof_lat,
            spoof_lon,
            self.target_lat,
            self.target_lon,
        )

        if error < self.hold_radius:
            self.state = "HOLD"

        if self.state == "APPROACH":

            dlat = self.target_lat - spoof_lat
            dlon = self.target_lon - spoof_lon

            norm = (dlat ** 2 + dlon ** 2) ** 0.5

            if norm > 0:

                self.glitch_x += self.step * dlat / norm
                self.glitch_y += self.step * dlon / norm

        return {

            "glitch_x": self.glitch_x,

            "glitch_y": self.glitch_y,

            "spoof_lat": spoof_lat,

            "spoof_lon": spoof_lon,

            "error": error,

            "state": self.state,

        }