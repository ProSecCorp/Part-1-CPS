from pymavlink import mavutil
import time


class GPSReader:

    def __init__(self, connection="udp:127.0.0.1:14549"):       #standard port:14549

        self.master = mavutil.mavlink_connection(connection)
        self.master.wait_heartbeat()

        print("GPSReader connesso")


    def get_position(self):

        while True:

            msg = self.master.recv_match(
                type="GLOBAL_POSITION_INT",
                blocking=True
            )

            if msg:

                return {
                    "time": time.time(),

                    "lat": msg.lat / 1e7,
                    "lon": msg.lon / 1e7,

                    "alt": msg.relative_alt / 1000,

                    "heading": msg.hdg / 100,

                }
                
    def get_raw_gps(self):
        latest_msg = None
        
        # 1. Drena tutti i pacchetti accumulati fino ad arrivare all'ultimo
        while True:
            msg = self.master.recv_match(type="GPS_RAW_INT", blocking=False)
            if msg is None:
                break
            if msg.fix_type >= 3:
                latest_msg = msg

        # 2. Se non c'erano pacchetti in buffer, aspetta quello nuovo in arrivo
        if latest_msg is None:
            while True:
                msg = self.master.recv_match(type="GPS_RAW_INT", blocking=True)
                if msg and msg.fix_type >= 3:
                    latest_msg = msg
                    break

        return {
            "lat": latest_msg.lat / 1e7,
            "lon": latest_msg.lon / 1e7,
            "alt": latest_msg.alt / 1000
        }