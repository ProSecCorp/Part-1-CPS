import time

from gps_reader.gps_reader import GPSReader
from controller.glitch_controller import GlitchController
from utils.logger import FlightLogger
from monitor.flight_monitor import FlightMonitor


GLITCH_X = 0      #max ~ 0.000032
GLITCH_Y = 0

ATTACK_TIME = 30

MIN_ALT = 10

TRACKED_EVENTS = [
    "AP: GPS Glitch or Compass error",
    "AP: EKF3 lane switch",
    "AP: EKF3 primary changed",
    "AP: Glitch cleared",
]


glitch = GlitchController()
gps = GPSReader()
monitor = FlightMonitor()

log = None


def log_position(event="", position=None):

    if position is None:
        position = gps.get_position()

    log.log(
        position,
        0,
        0,
        event
    )

    return position

choice = input(
    "Scegli tipo glitch (1=small, 2=big): "
).strip()

if choice == "1":
    GLITCH_X = 0.00003
    GLITCH_Y = 0
    ATTACK_TIME = 15
    log = FlightLogger("logs/constant_small_glitch.csv")
    print("Iniezione small glitch selezionata")
elif choice == "2":
    GLITCH_X = 0.00006
    GLITCH_Y = 0
    log = FlightLogger("logs/constant_big_glitch.csv")
    print("Iniezione big glitch selezionata")
else:
    print("Scelta non valida: inserisci 1 oppure 2")
    raise SystemExit(1)

land_seq = monitor.get_land_waypoint_seq()
if land_seq is None:
    print("! Attenzione !: Nessun waypoint LAND trovato nella missione o download fallito.")

monitor.wait_for_mode("AUTO")
log_position("ENTER_AUTO")

print("Inizio registrazione dati in modalità AUTO...")

#print("Attendo decollo")

start_attack = None
attack_active = False
attack_done = False

while True:
    # Controlla se il drone è arrivato al waypoint di atterraggio
    current_wp = monitor.get_current_waypoint_seq()
    if land_seq is not None and current_wp == land_seq:
        print(f"Raggiunto il waypoint di atterraggio (seq {land_seq}). Interruzione registrazione.")
        log_position("ENTER_LAND_WAYPOINT")
        break

    pos = gps.get_position()
    log_position(position=pos)

    for event in monitor.get_statustext_events(TRACKED_EVENTS):
        print(event)
        log_position(event, position=pos)

    # Avvio iniezione al superamento dell'altitudine minima
    if pos["alt"] > MIN_ALT and not attack_active and not attack_done:
        print("Altitudine minima superata: avvio iniezione glitch")
        log_position("ATTACK_START")
        start_attack = time.time()
        attack_active = True

    # Gestione timer iniezione
    if attack_active:
        if time.time() - start_attack < ATTACK_TIME:
            glitch.set_glitch(GLITCH_X, GLITCH_Y)
        else:
            print("Tempo iniezione terminato: reset glitch")
            glitch.reset()
            log_position("RESET")
            attack_active = False
            attack_done = True

    time.sleep(0.1)

# Cleanup finale
glitch.reset()
log.close()
print("Operazione completata e log salvato.")