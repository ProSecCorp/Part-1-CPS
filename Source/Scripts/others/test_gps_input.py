from pymavlink import mavutil
import time

print("Connessione a SITL...")

master = mavutil.mavlink_connection("udp:127.0.0.1:14550")
master.wait_heartbeat()

print("Heartbeat ricevuto")

lat = -35.363262 * 1e7
lon = 149.165237 * 1e7
alt = 584

print("Invio GPS_INPUT...")

while True:

    master.mav.gps_input_send(
        'time_usec' : 0,                        # (uint64_t) Timestamp (micros since boot or Unix epoch)
        'gps_id' : 0,                           # (uint8_t) ID of the GPS for multiple GPS inputs
        'ignore_flags' : 8,                     # (uint16_t) Flags indicating which fields to ignore (see GPS_INPUT_IGNORE_FLAGS enum). All other fields must be provided.
        'time_week_ms' : 0,                     # (uint32_t) GPS time (milliseconds from start of GPS week)
        'time_week' : 0,                        # (uint16_t) GPS week number
        'fix_type' : 3,                         # (uint8_t) 0-1: no fix, 2: 2D fix, 3: 3D fix. 4: 3D with DGPS. 5: 3D with RTK
        'lat' : 254100000,                              # (int32_t) Latitude (WGS84), in degrees * 1E7
        'lon' : 1212100000,                              # (int32_t) Longitude (WGS84), in degrees * 1E7
        'alt' : 60,                              # (float) Altitude (AMSL, not WGS84), in m (positive for up)
        'hdop' : 1,                             # (float) GPS HDOP horizontal dilution of position in m
        'vdop' : 1,                             # (float) GPS VDOP vertical dilution of position in m
        'vn' : 0,                               # (float) GPS velocity in m/s in NORTH direction in earth-fixed NED frame
        've' : 0,                               # (float) GPS velocity in m/s in EAST direction in earth-fixed NED frame
        'vd' : 0,                               # (float) GPS velocity in m/s in DOWN direction in earth-fixed NED frame
        'speed_accuracy' : 0,                   # (float) GPS speed accuracy in m/s
        'horiz_accuracy' : 0,                   # (float) GPS horizontal accuracy in m
        'vert_accuracy' : 0,                    # (float) GPS vertical accuracy in m
        'satellites_visible' : 7                # (uint8_t) Number of satellites visible.
    )

    time.sleep(0.1)
