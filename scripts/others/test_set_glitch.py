from pymavlink import mavutil
import time

PARAM_NAME = "SIM_GPS1_GLTCH_X"
NEW_VALUE = 10.0

print("Connessione...")

master = mavutil.mavlink_connection("udp:127.0.0.1:14550")
master.wait_heartbeat()

print("Heartbeat ricevuto")

# Scrive il parametro
master.mav.param_set_send(
    master.target_system,
    master.target_component,
    PARAM_NAME.encode("utf-8"),
    NEW_VALUE,
    mavutil.mavlink.MAV_PARAM_TYPE_REAL32
)

print(f"Richiesta inviata: {PARAM_NAME} = {NEW_VALUE}")

# Chiede di nuovo il parametro per verificarlo
time.sleep(0.5)

master.mav.param_request_read_send(
    master.target_system,
    master.target_component,
    PARAM_NAME.encode("utf-8"),
    -1
)

while True:
    msg = master.recv_match(type="PARAM_VALUE", blocking=True)

    if msg.param_id.rstrip("\x00") == PARAM_NAME:
        print(f"Valore letto: {msg.param_value}")
        break