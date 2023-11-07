"""
    Test
"""
from polyline import decode
from geopy.distance import geodesic
from math import radians, sin, cos, sqrt, atan2

def distancia_haversine_pasajero(coord1, coord2):
    """
    Calcula la distancia haversine entre dos coordenadas en metros.

    Args:
        coord1 (tuple): Coordenadas (latitud, longitud) del punto 1.
        coord2 (tuple): Coordenadas (latitud, longitud) del punto 2.

    Returns:
        float: Distancia haversine entre las coordenadas en metros.
    """
    # Radio de la Tierra en metros
    radio_t = 6371000.0
    # Convertir coordenadas de grados a radianes
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])
    # Diferencia de latitud y longitud
    diff_lat = lat2 - lat1
    dif__lon = lon2 - lon1
    # Calcular la distancia haversine
    dis_a = sin(diff_lat / 2)**2 + cos(lat1) * cos(lat2) * \
        sin(dif__lon / 2)**2
    circ = 2 * atan2(sqrt(dis_a), sqrt(1 - dis_a))
    distancia = radio_t * circ
    return distancia


def duracion_estimada_pasajero(distancia, vel_promedio):
    """
    Calcula la duración estimada en minutos dada una distancia y una velocidad promedio.

    Args:
        distancia (float): Distancia en metros.
        vel_promedio (float): Velocidad promedio en metros por segundo.

    Returns:
        float: Duración estimada en minutos.
    """
    # Distancia en metros, Velocidad promedio en metros por segundo
    duracion_seg = distancia / vel_promedio
    duracion_mins = duracion_seg / 60
    return duracion_mins


def duracion_estimada_ruta(route, vel_prom_km_h=30):
    """
    Calcula la duración estimada de una ruta en minutos.

    Utiliza la distancia entre los puntos de la ruta y la velocidad promedio
    proporcionada para calcular la duración estimada de la ruta.

    Args:
        route (list of tuples): Lista de coordenadas (latitud, longitud)
            que representan la ruta.
        velocidad_promedio_km_h (float): Velocidad promedio estimada
            del vehículo en kilómetros por hora.

    Retorna:
        float: Duración estimada de la ruta en minutos.
    """
    total_duracion_mins = 0

    for i in range(len(route) - 1):
        origin_coordinate = route[i]
        destination_coordinate = route[i + 1]
        distancia = distancia_haversine_pasajero(
            origin_coordinate, destination_coordinate)
        vel_prom_mps = vel_prom_km_h * 1000 / 3600  # Convertir km/h a m/s
        duracion_mins = duracion_estimada_pasajero(
            distancia, vel_prom_mps)
        total_duracion_mins += duracion_mins
    return total_duracion_mins


def calcular_distancia_lineal(row):
    """
    Calcula la distancia lineal entre dos puntos geográficos en un DataFrame.

    Esta función toma una fila del DataFrame que contiene información de los puntos de origen
    y destino y calcula la distancia lineal entre ellos utilizando el cálculo de geodesia.

    Args:
        row (pandas.Series): Una fila del DataFrame que contiene información de los puntos.

    Returns:
        float: La distancia lineal entre los puntos en kilómetros.

    Ejemplo:
        df['DISTANCIA_LINEAL'] = df.apply(calcular_distancia_lineal, axis=1)
    """
    origen = (row['LATITUD_ORIGEN'], row['LONGITUD_ORIGEN'])
    destino = (row['LATITUD_DESTINO'], row['LONGITUD_DESTINO'])
    distancia_km = geodesic(origen, destino).kilometers
    return distancia_km


def obtener_coordenadas_polilinea(directions_result):
    coords = []
    if directions_result:
        legs = directions_result[0]['legs'][0]['steps']
        for leg in legs:
            coords += decode(leg['polyline']['points'])
    return coords


def filtrar_coordenadas_por_distancia(row, polyline_coords, max_distancia_km):
    ref_coord = row['COORD_ORIGEN']
    is_near = False
    for coord in polyline_coords:
        distance = distancia_haversine(ref_coord[0], ref_coord[1], coord[0], coord[1])
        if distance <= max_distancia_km:
            is_near = True
            break
    return is_near


def distancia_haversine(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia Haversine entre dos puntos geográficos en coordenadas (latitud, longitud).

    Esta función toma las coordenadas de dos puntos y devuelve la distancia en kilómetros
    entre ellos utilizando la fórmula Haversine.

    Args:
        lat1 (float): Latitud del primer punto en grados.
        lon1 (float): Longitud del primer punto en grados.
        lat2 (float): Latitud del segundo punto en grados.
        lon2 (float): Longitud del segundo punto en grados.

    Returns:
        float: La distancia entre los dos puntos en kilómetros.

    Ejemplo:
        distancia = distancia_haversine(40.7128, -74.0060, 34.0522, -118.2437)
    """
    # Radio de la Tierra en kilómetros
    RADIO_TIERRA = 6371.0

    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    dis_a = sin(dlat / 2)**2 + cos(lat1_rad) * \
        cos(lat2_rad) * sin(dlon / 2)**2
    dis_c = 2 * atan2(sqrt(dis_a), sqrt(1 - dis_a))
    distance = RADIO_TIERRA * dis_c
    return distance
