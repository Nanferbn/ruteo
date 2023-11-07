"""
    google_maps.py
"""
from datetime import datetime
import googlemaps
from apps.ruteo.decoradores import contador
from apps.ruteo.constantes import GOOGLE_KEY


@contador
def calcular_ruta(origen, destino, waypoints=None,
    departure_time=datetime.now(), optimize=True):
    """
    Calcula la ruta entre un origen y un destino utilizando
        la API de Google Maps Directions.

    Args:
        origen (str or tuple): Ubicación de origen. Puede ser una
            dirección o una tupla (latitud, longitud).
        destino (str or tuple): Ubicación de destino. Puede ser una dirección
            o una tupla (latitud, longitud).
        waypoints (list): Lista opcional de ubicaciones intermedias
            (puntos intermedios) en la ruta.
        departure_time (datetime, optional): Hora de salida para estimar
            la duración. Por defecto es el momento actual.
        optimize (bool, optional): Indica si se deben optimizar los
            waypoints para la ruta. Por defecto es True.
    Returns:
        list: Lista de pasos de la ruta, cada uno representado como
            un diccionario con información detallada.
    Note:
        Asegúrate de tener una clave de API válida de Google Maps
            (GOOGLE_KEY) para utilizar esta función.
    Example:
        origen = "New York, NY"
        destino = "Los Angeles, CA"
        waypoints = ["Chicago, IL", "Dallas, TX"]
        ruta = calcular_ruta(origen, destino, waypoints)
        for step in ruta:
            print(step['html_instructions'])
    """
    gmaps = googlemaps.Client(key=GOOGLE_KEY)
    directions_result = gmaps.directions(
        origin=origen,
        destination=destino,
        waypoints=waypoints,
        departure_time=departure_time,
        optimize_waypoints=optimize
    )
    return directions_result