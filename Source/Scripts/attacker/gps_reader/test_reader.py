from gps_reader import GPSReader

gps = GPSReader()

while True:

    pos = gps.get_raw_gps()

    print(pos)