#!/usr/bin/env python3
import time
from pymavlink import mavutil

# 1. Porta su cui MAVProxy invia la telemetria completa
INPUT_CONN = 'udp:127.0.0.1:14549'

# 2. Porta UDP dedicata su cui vuoi inviare SOLO i messaggi GPS_RAW_INT
OUTPUT_CONN = 'udpout:127.0.0.1:14560'

print(f"In ascolto su {INPUT_CONN}...")
src = mavutil.mavlink_connection(INPUT_CONN)

print(f"Re-infrastrutturazione dati verso {OUTPUT_CONN}...")
dst = mavutil.mavlink_connection(OUTPUT_CONN, input=False)

while True:
    # Legge in modo bloccante solo i pacchetti GPS_RAW_INT
    msg = src.recv_match(type='GPS_RAW_INT', blocking=True)

    if msg:
        # Re-invia solo ed esattamente questo messaggio sulla nuova porta
        dst.mav.send(msg)