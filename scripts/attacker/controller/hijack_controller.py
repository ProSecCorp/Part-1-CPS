from utils.geo_utils import latlon_to_ne, clamp
import math

class HijackController:

    def __init__(
        self,
        target_lat,
        target_lon,
        kp=0.05,
        max_glitch=0.00003
    ):

        self.target_lat = target_lat
        self.target_lon = target_lon

        self.kp = kp
        self.max_glitch = max_glitch

    def compute_glitch(self, current_lat, current_lon):

        north, east = latlon_to_ne(
            self.target_lat,
            self.target_lon,
            current_lat,
            current_lon
        )

        # controllore proporzionale
        gx = self.kp * north / 111111.0

        gy = self.kp * east / (
            111111.0 *
            math.cos(math.radians(current_lat))
        )

        gx = clamp(
            gx,
            -self.max_glitch,
            self.max_glitch
        )

        gy = clamp(
            gy,
            -self.max_glitch,
            self.max_glitch
        )

        return gx, gy