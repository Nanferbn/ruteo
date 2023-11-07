"""
    tiempo.py
"""
import pandas as pd


def duracion_estimada_por_ruta_previa(df_group):
    """
        Calcula la duración estimada para una ruta previa específica.

        Esta función toma un grupo de datos de un DataFrame que contiene
            información sobre una ruta previa. Calcula la duración estimada
            de la ruta utilizando la función duracion_estimada_ruta y luego
            agrega esta duración calculada al DataFrame.

        Args:
            df_group (pd.DataFrame): Un grupo de datos que representa una ruta previa
                con información de origen, destinos y waypoints.

        Returns:
            pd.DataFrame: El DataFrame de entrada con una columna adicional
                'DURACION_CALCULADA' que contiene la duración estimada de la
                ruta en segundos.
    """
    destino_row = df_group.sample(n=1)
    print(f"Estimando duración de la ruta {destino_row['RUTA_PREVIA'].values[0]}")
    origenes = df_group[['LATITUD_ORIGEN', 'LONGITUD_ORIGEN']].values.tolist()
    origenes = [tuple(coord) for coord in origenes]
    # Obtener las coordenadas del punto de destino
    destino = (destino_row['LATITUD_DESTINO'].values[0], destino_row['LONGITUD_DESTINO'].values[0])
    origen, origenes_intermedios = encontrar_origen_mas_lejano(origenes, destino)
    puntos = [origen, *origenes_intermedios, destino]
    duracion_est = duracion_estimada_ruta(puntos)
    df_group['DURACION_CALCULADA'] = int(duracion_est)
    return df_group





def obtener_hora_salida(hora_maxima, fecha_str):
    """
    Calcula la hora de salida para un viaje, considerando una hora máxima y una duración máxima.

    Esta función toma una hora máxima en formato de 24 horas, una fecha en formato de cadena y calcula
    la hora de salida para un viaje considerando la hora máxima y la duración máxima del viaje.

    Args:
        hora_maxima (str): Hora máxima en formato de 24 horas (HH:MM).
        fecha_str (str): Fecha en formato de cadena (YYYY-MM-DD).

    Returns:
        datetime: La hora de salida calculada como un objeto datetime.

    Example:
        hora_maxima = "18:00"
        fecha_str = "2023-08-07"
        hora_salida = obtener_hora_salida(hora_maxima, fecha_str)
        print(hora_salida)
    """
    # Convertir la hora máxima a string
    hora_maxima_str = str(hora_maxima)
    # Concatenar la hora máxima con una fecha
    fecha_hora_str = fecha_str + " " + hora_maxima_str
    # Convertir la cadena a formato datetime
    fecha_hora = pd.to_datetime(fecha_hora_str)
    # Sumar una hora
    fecha_hora_sumada = fecha_hora - pd.DateOffset(minutes=10)
    return fecha_hora_sumada


def obtener_duracion_real_ruta(ruta):
    """
    Calcula la duración total real de una ruta previa en minutos.

    Esta función toma una lista de pasos de ruta previa y calcula la duración total real de la ruta sumando las duraciones
    de los pasos individuales. Luego, convierte la duración total de segundos a minutos y devuelve el valor.

    Args:
        ruta (list): Lista de pasos de la ruta previa, cada uno representado como un diccionario con información detallada.

    Returns:
        int: Duración total real de la ruta en minutos.

    Example:
        ruta_previa = [
            {'legs': [{'steps': [{'duration': {'value': 900}}]}]},
            {'legs': [{'steps': [{'duration': {'value': 1200}}]}]}
        ]
        duracion_total = obtener_duracion_real_ruta(ruta_previa)
        print(duracion_total)
    """
    total_duration = 0
    # Recorrer todos los trayectos y sumar las duraciones
    for route in ruta:
        legs = route['legs']
        for leg in legs:
            steps = leg['steps']
            for step in steps:
                duration_value = step['duration']['value']
                total_duration += duration_value
    # Convertir de segundos a minutos
    total_duration_minutes = total_duration // 60
    return total_duration_minutes


def duracion_real_por_ruta_previa(df_group):
    """
    Calcula la duración total real de una ruta previa en minutos.

    Esta función toma una lista de pasos de ruta previa y calcula la duración total real de la ruta sumando las duraciones
    de los pasos individuales. Luego, convierte la duración total de segundos a minutos y devuelve el valor.

    Args:
        ruta (list): Lista de pasos de la ruta previa, cada uno representado como un diccionario con información detallada.

    Returns:
        int: Duración total real de la ruta en minutos.

    Example:
        ruta_previa = [
            {'legs': [{'steps': [{'duration': {'value': 900}}]}]},
            {'legs': [{'steps': [{'duration': {'value': 1200}}]}]}
        ]
        duracion_total = obtener_duracion_real_ruta(ruta_previa)
        print(duracion_total)
    """
    print(f"Calculando duración real de la ruta {max(df_group['RUTA_PREVIA'])}")
    # Obtener la hora y fecha de la ruta:
    fecha_hora_viaje = obtener_hora_salida(
        df_group["HORA_SERVICIO_C"].max().time(), "2023-10-20")
    origenes = df_group[['LATITUD_ORIGEN', 'LONGITUD_ORIGEN']].values.tolist()
    origenes = [tuple(coord) for coord in origenes]
    # # Obtener las coordenadas del punto de destino
    destino_row = df_group.sample(n=1)
    destino = (destino_row['LATITUD_DESTINO'].values[0], destino_row['LONGITUD_DESTINO'].values[0])
    origen, origenes_intermedios = encontrar_origen_mas_lejano(origenes, destino)
    if len(origenes_intermedios) > 1:
        origenes_intermedios, ruta = ordenar_ruta(
            origen, origenes_intermedios, destino, fecha_hora_viaje)
    else:
        ruta = calcular_ruta(
            origen, destino, origenes_intermedios, fecha_hora_viaje, False)
    duracion = obtener_duracion_real_ruta(ruta)
    df_group['DURACION_REAL'] = duracion
    if duracion <= MAX_DURATION:
        orden_intermedios = ruta[0]['waypoint_order']
        for i, coordinate in enumerate(origenes_intermedios):
            validator_lat = df_group['LATITUD_ORIGEN'] == coordinate[0]
            validator_lon = df_group['LONGITUD_ORIGEN'] == coordinate[1]
            val = validator_lat & validator_lon
            df_group.loc[val, 'ORDEN_RECOGIDA'] = orden_intermedios[i] + 2
        validator_lat = df_group['LATITUD_ORIGEN'] == origen[0]
        validator_lon = df_group['LONGITUD_ORIGEN'] == origen[1]
        val = validator_lat & validator_lon
        df_group.loc[val, 'ORDEN_RECOGIDA'] = 1
        df_group['RUTA_VALIDA'] = 1
    return df_group
