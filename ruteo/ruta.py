"""
    ruta.py
"""
import numpy as np
import pandas as pd
from apps.ruteo.conexion import obtener_servicios
from apps.ruteo.preprocesamiento import (
    formato_dataframe, agrupar_por_destinos, agrupar_por_horas,
    obtener_ruta_previa)
from apps.ruteo.google_maps import calcular_ruta
from apps.ruteo.calculos import (
    calcular_distancia_lineal, obtener_coordenadas_polilinea,
    filtrar_coordenadas_por_distancia)
from apps.ruteo.tiempo import obtener_hora_salida
from sangabriel import settings


def encontrar_origen_mas_lejano(origenes, destino):
    """
    Encuentra el origen más lejano respecto al destino y retorna los demás
        origenes como intermedios.

    Calcula la distancia euclidiana entre los puntos de origen y el destino,
    identifica el origen más lejano y devuelve los demás origenes
        como intermedios.

    Arguments:
        origenes (list of tuples or array-like): Lista de coordenadas
            (latitud, longitud) que representan los puntos de origen.
        destino (tuple or array-like): Coordenadas (latitud, longitud) del destino.

    Returns:
        tuple: Una tupla con el origen más lejano respecto al destino y una
            lista de origenes intermedios.
    """
    origenes = np.array(origenes)
    destino = np.array(destino)
    # Calcular las distancias euclidianas entre los puntos de origen y el destino
    distancias_origenes = np.sqrt(np.sum((origenes[:, np.newaxis] - destino) ** 2, axis=2))
    # Encontrar el índice del origen más lejano respecto al destino
    indice_origen_mas_lejano = np.argmax(np.max(distancias_origenes, axis=1))
    # Obtener el origen más lejano y eliminarlo de la lista de origenes
    origen_mas_lejano = origenes[indice_origen_mas_lejano]
    origenes_intermedios = np.delete(origenes, indice_origen_mas_lejano, axis=0).tolist()
    origenes_intermedios = [tuple(coord) for coord in origenes_intermedios]
    return tuple(origen_mas_lejano), origenes_intermedios


def ordenar_ruta(origen, origenes_intermedios, destino, fecha_hora_viaje):
    """
    Ordena la ruta previa y devuelve los puntos intermedios en el orden optimizado.

    Esta función toma los puntos de origen, waypoints intermedios y destino, y calcula la ruta previa optimizada
    utilizando la función calcular_ruta. Luego, reordena los waypoints intermedios en el orden optimizado y devuelve tanto
    los waypoints reordenados como la ruta previa calculada.

    Args:
        origen (str or tuple): Ubicación de origen. Puede ser una dirección o una tupla (latitud, longitud).
        origenes_intermedios (list): Lista de ubicaciones intermedias (waypoints) en la ruta.
        destino (str or tuple): Ubicación de destino. Puede ser una dirección o una tupla (latitud, longitud).
        fecha_hora_viaje (datetime): Hora de salida para estimar la duración de la ruta.

    Returns:
        tuple: Una tupla que contiene dos elementos: 
            - La lista de waypoints intermedios reordenados en el orden optimizado.
            - La lista de pasos de la ruta previa, cada uno representado como un diccionario con información detallada.

    Note:
        Asegúrate de que la función calcular_ruta esté disponible y acepte los mismos argumentos.

    Example:
        origen = "New York, NY"
        origenes_intermedios = ["Chicago, IL", "Dallas, TX"]
        destino = "Los Angeles, CA"
        fecha_hora_viaje = datetime.now()
        origenes_ordenados, ruta_previa = ordenar_ruta(origen, origenes_intermedios, destino, fecha_hora_viaje)
        for step in ruta_previa:
            print(step['html_instructions'])
    """
    ruta_previa = calcular_ruta(
        origen, destino, origenes_intermedios, fecha_hora_viaje)
    np.insert(origenes_intermedios, 0, origen, axis=0)
    origenes_orden = ruta_previa[0]['waypoint_order']
    origenes_intermedios = [x for _, x in sorted(zip(origenes_orden, origenes_intermedios))]
    return origenes_intermedios, ruta_previa


def obtener_rutas_cercanas(df_servicios, servicio=0):
    """
    Procesa las rutas de los pasajeros a partir de un DataFrame de servicios.

    Args:
        df_servicios (pd.DataFrame): DataFrame con los servicios de pasajeros.
        servicio (int, opcional): Tipo de servicio a filtrar. 0 para
            'ida', 1 para 'retorno'.

    Returns:
        pd.DataFrame: DataFrame con las rutas de los pasajeros procesadas y ordenadas.
    """
    # Obtener las rutas de ida y formato de coordenadas
    df_rutas = obtener_pasajeros_ruta(df_servicios, servicio)
    df_rutas, df_error = formato_dataframe(df_rutas)
    if not df_rutas.empty:
        # Agrupar por destino y asignar etiquetas de grupo de destino
        df_rutas['GRUPO_DESTINO'] = agrupar_por_destinos(df_rutas)
        # Restablecer el índice y agrupar por horas
        df_rutas.reset_index(drop=True, inplace=True)
        df_rutas = agrupar_por_horas(df_rutas)
        # Ordenar por grupos de hora y destino
        df_rutas.sort_values(['GRUPO_HORA', 'GRUPO_DESTINO'], inplace=True)
        df_rutas.reset_index(drop=True, inplace=True)
        # Asignar rutas previas
        df_rutas = obtener_ruta_previa(df_rutas)
    return df_rutas, df_error


def obtener_pasajeros_ruta(df, servicio=0):
    """
    Filtra y devuelve los registros de pasajeros para una ruta específica en un DataFrame.

    Esta función toma un DataFrame de datos de pasajeros y filtra los registros para obtener
    los datos de una ruta específica, ya sea de ida o retorno, según el valor del parámetro
    'servicio'.

    Args:
        df (pandas.DataFrame): El DataFrame que contiene los datos de los pasajeros.
        servicio (int, opcional): Un valor que indica el tipo de servicio a filtrar.
            0 para ida y 1 para retorno. Por defecto, se considera ida (0).

    Returns:
        pandas.DataFrame: Un nuevo DataFrame con los registros filtrados correspondientes
        a la ruta especificada.

    Ejemplo:
        # Obtener registros de pasajeros para la ruta de ida
        df_ruta_ida = obtener_pasajeros_ruta(dataframe_pasajeros, servicio=0)

        # Obtener registros de pasajeros para la ruta de retorno
        df_ruta_retorno = obtener_pasajeros_ruta(dataframe_pasajeros, servicio=1)
    """
    tipo_servicio = 'ida' if servicio == 0 else 'retorno'
    validator = df['DETALLE_SERVICIO'].str.lower() == tipo_servicio
    rutas_ida = df[validator].copy()
    validator = rutas_ida['LATITUD_ORIGEN'] == ''
    rutas_ida.loc[validator, 'LATITUD_ORIGEN'] = None
    validator = rutas_ida['LATITUD_DESTINO'] == ''
    rutas_ida.loc[validator, 'LATITUD_DESTINO'] = None
    # Eliminar los registros sin coordenadas
    rutas_ida.dropna(subset=['LATITUD_ORIGEN', 'LATITUD_DESTINO'], inplace=True)
    return rutas_ida


def formato_coordenadas(df):
    """
    Aplica formato a las coordenadas y columnas temporales de un DataFrame.

    Esta función toma un DataFrame y realiza las siguientes transformaciones:
    - Convierte las columnas de coordenadas LATITUD_ORIGEN, LONGITUD_ORIGEN,
      LATITUD_DESTINO y LONGITUD_DESTINO a tipo de dato float.
    - Convierte la columna HORA_SERVICIO en formato de tiempo a tipo de dato datetime.
    - Ordena el DataFrame por CIUDAD_DESTINO y HORA_SERVICIO.

    Args:
        df (pandas.DataFrame): El DataFrame que se va a formatear.

    Returns:
        pandas.DataFrame: El DataFrame formateado con las transformaciones aplicadas.

    Ejemplo:
        df_formateado = formato_coordenadas(dataframe_original)
    """
    # Dando formato a las columnas:
    df['LATITUD_ORIGEN'] = df['LATITUD_ORIGEN'].astype(float)
    df['LONGITUD_ORIGEN'] = df['LONGITUD_ORIGEN'].astype(float)
    df['LATITUD_DESTINO'] = df['LATITUD_DESTINO'].astype(float)
    df['LONGITUD_DESTINO'] = df['LONGITUD_DESTINO'].astype(float)
    df['HORA_SERVICIO_C'] = pd.to_datetime(df['HORA_SERVICIO'], format='%H:%M:%S')
    df.sort_values(['CIUDAD_DESTINO', 'HORA_SERVICIO_C'], inplace=True)
    return df


def organizar_ruta(df_rutas):
    """
    Organiza un DataFrame de rutas en función de la distancia lineal y la ruta inicial.

    Esta función toma un DataFrame que contiene información sobre rutas y agrega una columna
    de distancia lineal calculada. Luego, organiza el DataFrame primero por ruta y luego
    por distancia lineal en orden descendente.

    Args:
        df_rutas (pandas.DataFrame): El DataFrame que se va a organizar.

    Returns:
        pandas.DataFrame: El DataFrame organizado.

    Ejemplo:
        df_rutas_organizado = organizar_ruta(dataframe_rutas)
    """
    df_rutas['DISTANCIA_LINEAL'] = df_rutas.apply(calcular_distancia_lineal, axis=1)
    df_rutas.sort_values(by=['RUTA_INICIAL', 'DISTANCIA_LINEAL'],
                         ascending=[True, False], inplace=True)
    df_rutas.reset_index(drop=True, inplace=True)
    return df_rutas


def obtener_rutas_ida(df_servicio, max_distancia_km=2):
    """
    Esta función procesa un DataFrame de servicios de transporte y calcula las rutas de ida de los vehículos
    basándose en la información de coordenadas y hora de salida. Las rutas se agrupan en función de su proximidad
    y se etiquetan con identificadores únicos.

    Args:
        df_servicio (pandas.DataFrame): DataFrame que contiene información de servicios de transporte.

    Returns:
        pandas.DataFrame, pandas.DataFrame:
            - Un DataFrame con las rutas de ida de los vehículos, incluyendo información de ruta inicial y final.
            - Un DataFrame que almacena cualquier error que ocurra durante el proceso.

    Esta función utiliza las siguientes funciones auxiliares: obtener_rutas_cercanas, organizar_ruta,
    obtener_hora_salida, calcular_ruta, obtener_coordenadas_polilinea y filtrar_coordenadas_por_distancia.
    """
    df_ida, df_error = obtener_rutas_cercanas(df_servicio)
    if not df_ida.empty:
        df_ida['RUTA_INICIAL'] = df_ida['RUTA_PREVIA'].copy()
        df_ida = organizar_ruta(df_ida)
        # Calcular las rutas por hora de llegada y destino en común
        df_ida['COORD_ORIGEN'] = list(
            zip(df_ida['LATITUD_ORIGEN'], df_ida['LONGITUD_ORIGEN']))
        df_ida['COORD_DESTINO'] = list(
            zip(df_ida['LATITUD_DESTINO'], df_ida['LONGITUD_DESTINO']))
        for valor in df_ida['RUTA_INICIAL'].unique().tolist():
            validator = df_ida['RUTA_INICIAL'] == valor
            df_ruta = df_ida[validator].copy()
            print(f"Calculando ruta {valor} con {df_ruta.shape[0]} pasajeros.")
            ruta_test = df_ruta.copy()
            count = 1
            fecha_hora_viaje = obtener_hora_salida(
                df_ruta["HORA_SERVICIO_C"].max().time(), "2023-11-04")
            while not ruta_test.empty:
                primer_valor = ruta_test.iloc[0]
                origen = (primer_valor['LATITUD_ORIGEN'], primer_valor['LONGITUD_ORIGEN'])
                destino = (primer_valor['LATITUD_DESTINO'], primer_valor['LONGITUD_DESTINO'])
                directions_result = calcular_ruta(origen, destino, None, fecha_hora_viaje)
                poly_coords = obtener_coordenadas_polilinea(directions_result)

                ruta_test['SE_AGRUPA'] = ruta_test.apply(
                    filtrar_coordenadas_por_distancia, axis=1, args=(poly_coords, max_distancia_km))
                validator_index = df_ida.index.isin(ruta_test[ruta_test['SE_AGRUPA']].index)
                df_ida.loc[validator_index, 'RUTA_FINAL'] = f"{str(primer_valor['RUTA_INICIAL'])}_{count}"
                ruta_test = ruta_test[~ruta_test['SE_AGRUPA']].copy()
                if ruta_test.shape[0] == 1:
                    ruta_test = pd.DataFrame()
                count += 1

        df_ida.sort_values(by=['RUTA_INICIAL', 'RUTA_FINAL', 'DISTANCIA_LINEAL'],
                                ascending=[True, True, False], inplace=True)
        df = df_ida.copy()
    else:
        df = pd.DataFrame()
    return df, df_error


def servicios_completos(
        fecha_inicio, fecha_final, tipo_prod_id=14, tiempo_aprox=30):
    max_distancia_km = (1/15)*tiempo_aprox
    df_servicios = obtener_servicios(fecha_inicio, fecha_final, tipo_prod_id)
    df_servicios = df_servicios[df_servicios['CIUDAD_ID_ORIGEN'] == 104].copy()
    df_rutas_ida = pd.DataFrame()
    for valor in df_servicios['FECHA_SERVICIO'].unique().tolist():
        validator = df_servicios['FECHA_SERVICIO'] == valor
        df_dia = df_servicios[validator].copy()
        print(f"Calculando rutas fecha: {valor} con {df_dia.shape[0]} pasajeros")
        df_ida, _ = obtener_rutas_ida(df_dia, max_distancia_km)
        if not df_ida.empty:
            df_ida['RUTA_FINAL'] = "-".join(valor.split("-")[1:]) + \
                "_" + df_ida['RUTA_FINAL']
            df_rutas_ida = pd.concat([df_rutas_ida, df_ida], axis=0)
    df_retorno, _ = obtener_rutas_cercanas(df_servicios, 1)
    df_retorno = df_retorno[df_retorno['CIUDAD_ID_ORIGEN'] == 104].copy()
    df_ruta_ida = df_rutas_ida[
        ['IDENTIFICACION_USUARIO', 'FECHA_SERVICIO', 'RUTA_FINAL']].copy()
    df_rutas_retorno = df_retorno.merge(
        df_ruta_ida, on=['IDENTIFICACION_USUARIO', 'FECHA_SERVICIO'], how='left')
    return df_rutas_ida, df_rutas_retorno
