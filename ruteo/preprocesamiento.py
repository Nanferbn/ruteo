"""
    pre.py
"""
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import haversine_distances

def obtener_pasajeros_ruta(df_servicios, servicio=0):
    """
    Filtra los datos del DataFrame de servicios para obtener los
    registros correspondientes a un tipo de servicio específico
    (ida o retorno) y eliminar aquellos registros que no contengan
    coordenadas de origen o destino.

    Args:
        df_servicios (pd.DataFrame): DataFrame que contiene los
            datos de los servicios.
        servicio (int, opcional): Tipo de servicio a filtrar. 0 para
            'ida', 1 para 'retorno'.

    Returns:
        pd.DataFrame: Un nuevo DataFrame con los registros
            filtrados y sin registros sin coordenadas.

    Example:
        df_servicios = obtener_servicios('04-27-2023')
        df_ida = obtener_pasajeros_ruta(df_servicios, servicio=0)
        # df_ida ahora contiene solo los registros de servicios
            de ida con coordenadas válidas.
    """
    tipo_servicio = 'ida' if servicio == 0 else 'retorno'
    validator = df_servicios['DETALLE_SERVICIO'].str.lower() == tipo_servicio
    pasajeros_por_tipo = df_servicios[validator].copy()
    # Se limpian los datos de coordenadas para ser omitidos más adelante
    validator = pasajeros_por_tipo['LATITUD_ORIGEN'] == ''
    pasajeros_por_tipo.loc[validator, 'LATITUD_ORIGEN'] = None
    validator = pasajeros_por_tipo['LATITUD_DESTINO'] == ''
    pasajeros_por_tipo.loc[validator, 'LATITUD_DESTINO'] = None
    return pasajeros_por_tipo


def formato_dataframe(df_pasajeros):
    """
    Realiza el preprocesamiento básico de un DataFrame
    para las columnas relevantes.

    Esta función convierte las columnas 'LATITUD_ORIGEN' y 'LATITUD_DESTINO'
        a tipo float, y la columna 'HORA_SERVICIO' a formato datetime.
        Luego, ordena el DataFrame por 'CIUDAD_DESTINO' y 'HORA_SERVICIO_C'.

    Args:
        df_pasajeros (pd.DataFrame): El DataFrame que contiene
            los datos a pre-procesar.

    Retorna:
        tuple: 
            pd.DataFrame: DataFrame con las columnas relevantes pre-procesadas,
            pd.DataFrame: DataFrame con los registros que no tienen coordenadas
                para ser notificados.
    """
    # Revisar pasajeros sin coordenadas
    validator_empty = (df_pasajeros['LATITUD_ORIGEN'].isnull()) | \
        (df_pasajeros['LATITUD_DESTINO'].isnull())
    df_faltantes = df_pasajeros[validator_empty].copy()
    # Se eliminan estos pasajeros:
    df_pasajeros.dropna(subset=['LATITUD_ORIGEN', 'LATITUD_DESTINO'], inplace=True)
    # Convertir las columnas de coordenadas a tipo float
    df_pasajeros['LATITUD_ORIGEN'] = df_pasajeros[
        'LATITUD_ORIGEN'].astype(float)
    df_pasajeros['LONGITUD_ORIGEN'] = df_pasajeros[
        'LONGITUD_ORIGEN'].astype(float)
    df_pasajeros['LATITUD_DESTINO'] = df_pasajeros[
        'LATITUD_DESTINO'].astype(float)
    df_pasajeros['LONGITUD_DESTINO'] = df_pasajeros[
        'LONGITUD_DESTINO'].astype(float)

    # Convertir la columna 'HORA_SERVICIO' a formato datetime
    df_pasajeros['HORA_SERVICIO_C'] = pd.to_datetime(
        df_pasajeros['HORA_SERVICIO'], format='%H:%M:%S')

    # Ordenar el DataFrame por 'CIUDAD_DESTINO' y 'HORA_SERVICIO_C'
    df_pasajeros.sort_values(['CIUDAD_DESTINO', 'HORA_SERVICIO_C'], inplace=True)

    return df_pasajeros, df_faltantes


def agrupar_por_destinos(df_pasajeros):
    """
    Realiza la agrupación de coordenadas por destinos cercanos,
    en dado caso de que las coordenadas en el mismo destino varien un 
    poco (100 metros).

    Args:
        df_pasajeros (pd.DataFrame): DataFrame que contiene las
            coordenadas de destino.
    Returns:
        np.ndarray: Un arreglo con las etiquetas de los clusters
            asignadas a cada punto.
    """
    # Seleccionar las columnas de LATITUD_DESTINO y LONGITUD_DESTINO
    destinos = df_pasajeros[['LATITUD_DESTINO', 'LONGITUD_DESTINO']]
    # Convertir las coordenadas a radianes
    destinos_rad = np.radians(destinos.to_numpy())
    # Calcular la matriz de distancias utilizando la fórmula de Haversine
    distancias = haversine_distances(destinos_rad) * 6371000  # Radio de la Tierra en metros
    # Aplicar el algoritmo de DBSCAN
    epsilon = 100  # Umbral de distancia para considerar puntos vecinos (100 metros)
    min_samples = 1  # Número mínimo de puntos para formar un grupo
    dbscan = DBSCAN(eps=epsilon, min_samples=min_samples, metric='precomputed')
    labels = dbscan.fit_predict(distancias)
    return labels


def agrupar_por_horas(df_pasajeros):
    """
        Asigna grupos de horas a un DataFrame según la diferencia
        de tiempo entre registros.

    Args:
        df_pasajeros (pd.DataFrame): DataFrame con las columnas 'HORA_SERVICIO_C'
            que contienen la hora de servicio.

    Retorna:
        pd.DataFrame: DataFrame con una nueva columna 'GRUPO_HORA'
            que indica el grupo de hora asignado.
    """
    ruta = 0
    max_mins = 10
    df_pasajeros['GRUPO_HORA'] = None
    hora = df_pasajeros.loc[0, 'HORA_SERVICIO_C']
    for indice, row in df_pasajeros.iterrows():
        hora_actual = row['HORA_SERVICIO_C']
        diff_hora = hora_actual - hora
        # Si la diferencia de tiempo es negativa, convertirla a positiva
        if diff_hora < pd.Timedelta(0):
            diff_hora = hora - hora_actual
        # Si la diferencia de tiempo es mayor a max_mins, se inicia un nuevo grupo
        if diff_hora > pd.Timedelta(minutes=max_mins):
            hora = hora_actual
            ruta += 1
        df_pasajeros.loc[indice, 'GRUPO_HORA'] = ruta

    return df_pasajeros


def obtener_ruta_previa(df_pasajeros):
    """
    Asigna rutas previas a un DataFrame en función de los
        grupos de hora y destino.

    Args:
        df_pasajeros (pd.DataFrame): DataFrame con columnas 'GRUPO_HORA'
            y 'GRUPO_DESTINO' que representan los grupos.

    Returns:
        - pd.DataFrame: DataFrame con una nueva columna 'RUTA_PREVIA'
            que indica la ruta previa asignada.
    """
    ruta = 0
    grupo_hora = 0
    grupo_destino = 0
    df_pasajeros['RUTA_PREVIA'] = None
    for indice, row in df_pasajeros.iterrows():
        hora_actual = row['GRUPO_HORA']
        destino_actual = row['GRUPO_DESTINO']
        val_1 = grupo_hora == hora_actual
        val_2 = grupo_destino == destino_actual
        if not (val_1 and val_2):
            ruta += 1
        df_pasajeros.loc[indice, 'RUTA_PREVIA'] = ruta
        grupo_hora = hora_actual
        grupo_destino = destino_actual
    return df_pasajeros
