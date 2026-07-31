from pymavlink import mavutil

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
master.wait_heartbeat()

print("Connected!")

while True:
    msg = master.recv_match(
        type='GLOBAL_POSITION_INT',
        blocking=True
    )
    print(msg.lat, msg.lon)
