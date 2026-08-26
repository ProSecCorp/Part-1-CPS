import time

from gps_reader.gps_reader import GPSReader
from controller.glitch_controller import GlitchController
from utils.logger import FlightLogger
from monitor.flight_monitor import FlightMonitor


GLITCH_X = 0      #max ~ 0.000032
GLITCH_Y = 0

ATTACK_TIME = 15

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
    "Choose glitch type (1=small, 2=big): "
).strip()

if choice == "1":
    GLITCH_X = 0.00003
    GLITCH_Y = 0
    ATTACK_TIME = 15
    log = FlightLogger("logs/constant_small_glitch.csv")
    print("Small glitch injection selected")
elif choice == "2":
    GLITCH_X = 0.00006
    GLITCH_Y = 0
    log = FlightLogger("logs/constant_big_glitch.csv")
    print("Big glitch injection selected")
else:
    print("Invalid choice: please enter 1 or 2")
    raise SystemExit(1)

land_seq = monitor.get_land_waypoint_seq()
if land_seq is None:
    print("! Attention !: No LAND waypoint found in the mission or download failed.")

monitor.wait_for_mode("AUTO")
log_position("ENTER_AUTO")

print("Start recording data in AUTO mode...")

#print("Waiting for takeoff")

start_attack = None
attack_active = False
attack_done = False

while True:
    # Controlla se il drone è arrivato al waypoint di atterraggio
    current_wp = monitor.get_current_waypoint_seq()
    if land_seq is not None and current_wp == land_seq:
        print(f"Landing waypoint reached (seq {land_seq}). Stopping recording.")
        log_position("ENTER_LAND_WAYPOINT")
        break

    pos = gps.get_position()
    log_position(position=pos)

    for event in monitor.get_statustext_events(TRACKED_EVENTS):
        print(event)
        log_position(event, position=pos)

    # Avvio iniezione al superamento dell'altitudine minima
    if pos["alt"] > MIN_ALT and not attack_active and not attack_done:
        print("Minimum altitude reached: starting glitch injection")
        log_position("ATTACK_START")
        start_attack = time.time()
        attack_active = True

    # Gestione timer iniezione
    if attack_active:
        if time.time() - start_attack < ATTACK_TIME:
            glitch.set_glitch(GLITCH_X, GLITCH_Y)
        else:
            print("Injection time completed: resetting glitch")
            glitch.reset()
            log_position("RESET")
            attack_active = False
            attack_done = True

    time.sleep(0.1)

# Cleanup finale
glitch.reset()
log.close()
print("Operation completed and log saved. Program finished.")