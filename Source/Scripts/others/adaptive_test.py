import time
from controller.glitch_controller import GlitchController
from gps_reader.gps_reader import GPSReader

glitch = GlitchController()
gps = GPSReader()

# Coordinate di partenza (WP Missione / Home)
WP_START_LAT, WP_START_LON = -35.3632621, 149.1652374

# Coordinate di arrivo teoriche (Dalla Missione)
WP_LAND_LAT, WP_LAND_LON = -35.359530, 149.160738

# Coordinate di arrivo reali desiderate
REAL_TARGET_LAT, REAL_TARGET_LON = -35.362161, 149.160089

# Calcolo glitch finale
TARGET_GLITCH_LAT = REAL_TARGET_LAT - WP_LAND_LAT  # -0.002631
TARGET_GLITCH_LON = REAL_TARGET_LON - WP_LAND_LON  # -0.000649

# Parametri temporali del volo
ESTIMATED_FLIGHT_TIME = 120  # Durata stimata in secondi
UPDATE_INTERVAL = 0.5        # Frequenza di aggiornamento in secondi
STEPS = int(ESTIMATED_FLIGHT_TIME / UPDATE_INTERVAL)

# Incremento per singolo step
step_lat = TARGET_GLITCH_LAT / STEPS
step_lon = TARGET_GLITCH_LON / STEPS

current_glitch_lat = 0.0
current_glitch_lon = 0.0

print("Avvio iniezione progressiva del glitch...")

for i in range(STEPS):
    current_glitch_lat += step_lat
    current_glitch_lon += step_lon

    # Imposta il glitch sul controller (adatta in base ai parametri accettati)
    glitch.set_glitch(current_glitch_lon, current_glitch_lat)

    # Leggi la posizione GPS pulendo il buffer
    pos = gps.get_raw_gps()
    
    print(f"Step {i+1}/{STEPS} - Glitch Lat: {current_glitch_lat:.7f} | Lon: {current_glitch_lon:.7f}")
    time.sleep(UPDATE_INTERVAL)

print("Iniezione completata. Raggiunto il valore target per il Land.")