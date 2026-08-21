import math

EARTH_RADIUS = 6371000


def meters_to_lat(m):
    return m / 111111


def meters_to_lon(m, lat):
    return m / (111111 * math.cos(math.radians(lat)))


def distance(lat1, lon1, lat2, lon2):

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = (
        math.sin(dp / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dl / 2) ** 2
    )

    return EARTH_RADIUS * 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a),
    )


def bearing(lat1, lon1, lat2, lon2):

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    dlon = math.radians(lon2 - lon1)

    x = math.sin(dlon) * math.cos(lat2)

    y = (
        math.cos(lat1) * math.sin(lat2)
        - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    )

    return math.atan2(x, y)


def move(lat, lon, distance_m, heading):

    d = distance_m / EARTH_RADIUS

    lat1 = math.radians(lat)
    lon1 = math.radians(lon)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(d)
        + math.cos(lat1) * math.sin(d) * math.cos(heading)
    )

    lon2 = lon1 + math.atan2(
        math.sin(heading) * math.sin(d) * math.cos(lat1),
        math.cos(d) - math.sin(lat1) * math.sin(lat2),
    )

    return (
        math.degrees(lat2),
        math.degrees(lon2),
    )
    
GPS_GLITCH_RADIUS = 5.0      # metri
GPS_GLITCH_ACCEL = 10.0      # m/s²
    
def allowed_jump(dt):

    return max(
        GPS_GLITCH_RADIUS,
        GPS_GLITCH_ACCEL * dt * dt
    )