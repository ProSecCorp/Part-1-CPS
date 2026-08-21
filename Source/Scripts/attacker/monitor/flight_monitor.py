import time
from pymavlink import mavutil

class FlightMonitor:
    def __init__(self, connection="udp:127.0.0.1:14548"):
    
            self.master = mavutil.mavlink_connection(connection)
            self.master.wait_heartbeat()
    
            print("FlightMonitor connesso")

    def get_current_mode(self):
        """
        Legge in modo non bloccante i messaggi HEARTBEAT e restituisce 
        la modalità di volo corrente (es. 'AUTO', 'LAND', 'LOITER'), 
        oppure None se non ci sono nuovi messaggi.
        """
        msg = self.master.recv_match(type='HEARTBEAT', blocking=False)
        if msg and msg.get_srcSystem() == self.master.target_system:
            return self.master.flightmode
        return None

    def wait_for_mode(self, target_mode, check_interval=0.5):
        """
        Blocca l'esecuzione finché il drone non entra nella modalità richiesta.
        """
        print(f"In attesa della modalità: {target_mode}...")
        while True:
            msg = self.master.recv_match(type='HEARTBEAT', blocking=True, timeout=1.0)
            if msg and msg.get_srcSystem() == self.master.target_system:
                current_mode = self.master.flightmode
                if current_mode == target_mode:
                    print(f"Modalità {target_mode} raggiunta!")
                    return True
            time.sleep(check_interval)
            
    def get_land_waypoint_seq(self, timeout=10):
        """
        Richiede la lista dei waypoint e restituisce l'indice (seq) 
        del primo waypoint con comando MAV_CMD_NAV_LAND (ID 21).
        """
        print("Richiesta lista waypoint alla Ground Station / Autopilota...")
        self.master.waypoint_request_list_send()
        
        # Attende il messaggio MISSION_COUNT
        msg = self.master.recv_match(type='MISSION_COUNT', blocking=True, timeout=timeout)
        if not msg:
            print("⚠️ Impossibile scaricare il numero di waypoint (Timeout).")
            return None
        
        count = msg.count
        print(f"Trovati {count} waypoint nella missione.")

        land_seq = None
        for i in range(count):
            # Usiamo la versione _INT esplicita per evitare l'avviso di ArduPilot
            self.master.mav.mission_request_int_send(
                self.master.target_system,
                self.master.target_component,
                i
            )
            
            # Ascoltiamo sia MISSION_ITEM_INT che MISSION_ITEM
            item = self.master.recv_match(
                type=['MISSION_ITEM_INT', 'MISSION_ITEM'], 
                blocking=True, 
                timeout=timeout
            )
            
            if item:
                # 21 = MAV_CMD_NAV_LAND
                if item.command == mavutil.mavlink.MAV_CMD_NAV_LAND:
                    land_seq = item.seq
                    print(f"Waypoint di atterraggio (NAV_LAND) trovato all'indice: {land_seq}")
                    break

        return land_seq

    def get_current_waypoint_seq(self):
        """
        Legge in modo non bloccante l'indice del waypoint attualmente in esecuzione.
        """
        msg = self.master.recv_match(type='MISSION_CURRENT', blocking=False)
        if msg and msg.get_srcSystem() == self.master.target_system:
            return msg.seq
        return None
    
    def get_current_waypoint_position(self):
        """
        Legge in modo non bloccante la posizione del waypoint attualmente in esecuzione.
        """
        current_seq = self.get_current_waypoint_seq()
        if current_seq is None:
            return None
        
        # Richiedi il waypoint corrente
        self.master.mav.mission_request_int_send(
            self.master.target_system,
            self.master.target_component,
            current_seq
        )
        
        # Ascolta il messaggio MISSION_ITEM_INT o MISSION_ITEM
        item = self.master.recv_match(
            type=['MISSION_ITEM_INT', 'MISSION_ITEM'], 
            blocking=True, 
            timeout=1.0
        )
        
        if item:
            return {
                "lat": item.x / 1e7,  # Converti da int32_t a gradi decimali
                "lon": item.y / 1e7,  # Converti da int32_t a gradi decimali
                "alt": item.z         # Altitudine in metri (float)
            }
        
        return None
    
    def wait_for_next_waypoint(self, current_seq, check_interval=0.5):
        """
        Blocca l'esecuzione finché il drone non passa al waypoint successivo.
        """
        print(f"In attesa del passaggio dal waypoint {current_seq} al successivo...")
        while True:
            msg = self.master.recv_match(type='MISSION_CURRENT', blocking=True, timeout=1.0)
            if msg and msg.get_srcSystem() == self.master.target_system:
                if msg.seq != current_seq:
                    print(f"Passato al waypoint {msg.seq}.")
                    return msg.seq
            time.sleep(check_interval)

    def get_statustext_events(self, patterns):
        """
        Legge tutti i messaggi STATUSTEXT disponibili e restituisce solo
        quelli che contengono una delle stringhe richieste.
        """
        matches = []

        normalized_patterns = []
        for pattern in patterns:
            normalized_patterns.append(pattern.lower())
            if pattern.startswith("AP: "):
                normalized_patterns.append(pattern[4:].lower())

        while True:
            msg = self.master.recv_match(type='STATUSTEXT', blocking=False)
            if not msg:
                break

            if msg.get_srcSystem() != self.master.target_system:
                continue

            text = msg.text
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')

            text = text.rstrip('\x00')
            normalized_text = text.lower()

            for pattern in normalized_patterns:
                if pattern in normalized_text:
                    matches.append(text)
                    break

        return matches
    
    def get_current_air_speed(self):
        """
        Legge in modo non bloccante la velocità aerea corrente (airspeed).
        """
        msg = self.master.recv_match(type='VFR_HUD', blocking=False)
        if msg and msg.get_srcSystem() == self.master.target_system:
            return msg.airspeed
        return 0