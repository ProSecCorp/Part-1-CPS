from pymavlink import mavutil
import math
import time

# -----------------------------
# TARGET SPOOFATO
# -----------------------------
target_lat = -35.36047599
target_lon = 149.16507051
target_alt = 40.0   # altitudine reale del drone

step_size = 1.0     # metri per step
delay = 0.1         # secondi tra step

# -----------------------------
# CONNESSIONE A SITL
# -----------------------------
master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()
print("Connesso a SITL")

# -----------------------------
# FUNZIONI UTILI
# -----------------------------
def set_param(name, value):
    master.mav.param_set_send(
        master.target_system,
        master.target_component,
        name.encode(),
        float(value),
        mavutil.mavlink.MAV_PARAM_TYPE_REAL32
    )

def get_current_gps():
    msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    lat = msg.lat / 1e7
    lon = msg.lon / 1e7
    alt = msg.alt / 1000.0
    return lat, lon, alt

def ned_offset(lat1, lon1, lat2, lon2):
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    north = dlat * 111320
    east = dlon * 111320 * math.cos(math.radians(lat1))
    return north, east

# -----------------------------
# MOVIMENTO VERSO TARGET SPOOFATO
# -----------------------------
print("Inizio spoofing verso il target...")

while True:
    # 1) Leggi posizione attuale
    cur_lat, cur_lon, cur_alt = get_current_gps()

    # 2) Calcola offset NED verso il target
    north, east = ned_offset(cur_lat, cur_lon, target_lat, target_lon)
    dist = math.sqrt(north**2 + east**2)

    print(f"Distanza al target: {dist:.1f} m")

    # 3) Se vicino al target → STOP
    if dist < 2.0:
        print("Target spoofato raggiunto!")
        break

    # 4) Normalizza per step
    scale = step_size / dist
    step_n = north * scale
    step_e = east * scale

    # 5) Applica glitch incrementale (Z=0)
    set_param("SIM_GPS1_GLITCH_X", step_n)
    set_param("SIM_GPS1_GLITCH_Y", step_e)
    set_param("SIM_GPS1_GLITCH_Z", 0)

    time.sleep(delay)

print("\nIl drone crede di essere nel punto del LAND → ArduPilot atterrerà qui.")