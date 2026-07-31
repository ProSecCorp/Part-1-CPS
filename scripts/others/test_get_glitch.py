from pymavlink import mavutil

master = mavutil.mavlink_connection("udp:127.0.0.1:14550")
master.wait_heartbeat()

print("Connesso")

master.mav.param_request_read_send(
    master.target_system,
    master.target_component,
    b"SIM_GPS1_GLTCH_X",
    -1
)

while True:
    msg = master.recv_match(type="PARAM_VALUE", blocking=True)

    if msg.param_id.strip("\x00") == "SIM_GPS1_GLTCH_X":
        print(msg)
        break
