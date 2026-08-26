from pymavlink import mavutil
import time


class GlitchController:
    """
    Gestisce i parametri:
        SIM_GPS1_GLTCH_X
        SIM_GPS1_GLTCH_Y
    """

    def __init__(self, connection="udp:127.0.0.1:14550"):

        #print("Connessione ad ArduPilot...")

        self.master = mavutil.mavlink_connection(connection)
        self.master.wait_heartbeat()

        print("GlitchController connected.")

    def _set_parameter(self, name, value):

        self.master.mav.param_set_send(
            self.master.target_system,
            self.master.target_component,
            name.encode(),
            float(value),
            mavutil.mavlink.MAV_PARAM_TYPE_REAL32
        )

    def _read_parameter(self, name):

        self.master.mav.param_request_read_send(
            self.master.target_system,
            self.master.target_component,
            name.encode(),
            -1
        )

        while True:

            msg = self.master.recv_match(
                type="PARAM_VALUE",
                blocking=True
            )

            if msg.param_id.rstrip("\x00") == name:
                return msg.param_value

    def set_glitch(self, x, y):

        self._set_parameter("SIM_GPS1_GLTCH_X", x)
        self._set_parameter("SIM_GPS1_GLTCH_Y", y)

    def get_glitch(self):

        x = self._read_parameter("SIM_GPS1_GLTCH_X")
        y = self._read_parameter("SIM_GPS1_GLTCH_Y")

        return x, y

    def reset(self):

        self.set_glitch(0.0, 0.0)