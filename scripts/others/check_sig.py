from pymavlink import mavutil

master = mavutil.mavlink_connection('udp:127.0.0.1:14550')

print(master.mav.gps_input_send.__doc__)

