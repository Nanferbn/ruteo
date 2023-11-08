import os
import paramiko
import pandas as pd
import psycopg2
from apps.ruteo.constantes import (SSH_HOST, SSH_USERNAME, SSH_KEY_PATH,
                        DB_NAME, DB_USER, DB_PASSWORD, DB_HOST,
                        DB_PORT, DB_SCHEMA, DEBUG, PROD_DATA, ABSOLUTE_PATH)


def obtener_servicios(fecha_inicio, fecha_final=None, tipo_prod_list=[14]):
    """
    Obtiene datos de servicios en un rango de fechas desde la base de datos.

    Args:
        fecha_inicio (str): Fecha de inicio en formato 'YYYY-MM-DD'.
        fecha_final (str, opcional): Fecha final en formato 'YYYY-MM-DD'.
            Si no se proporciona, se asume la fecha de inicio.

    Returns:
        pd.DataFrame: DataFrame que contiene los resultados de la consulta.
    """
    tipo_prod = ",".join(tipo_prod_list)
    conn = Connection(PROD_DATA)
    QUERY_FILE = 'obtain_services'
    QUERY_FILE = QUERY_FILE if not DEBUG else QUERY_FILE + '_test'
    if not fecha_final:
        fecha_final = fecha_inicio
    df_data = conn.execute_query(
        QUERY_FILE, [fecha_inicio, fecha_final, tipo_prod])
    conn.close()
    return df_data


class Connection:
    """
    Clase para manejar la conexión a bases de datos PostgreSQL.
    
    Args:
        ssh_connection (bool): Indica si se debe establecer una conexión SSH
            antes de la conexión a la base de datos.

    Attributes:
        conn (psycopg2.extensions.connection): Conexión a la base de datos PostgreSQL.
        ssh (bool): Indica si se ha establecido una conexión SSH.
    """
    def __init__(self, ssh_connection=False):
        """
        Inicializa una instancia de la clase Connection.

        Args:
            ssh_connection (bool): Indica si se debe establecer
                una conexión SSH antes de la conexión a la base de datos.
        """
        conn_port = self.ssh_connection(DB_PORT) if ssh_connection else DB_PORT
        self.conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=conn_port
        )
        self.ssh = ssh_connection

    def ssh_connection(self, pg_port=5432):
        """
        Establece una conexión SSH antes de la conexión a la base
            de datos PostgreSQL.

        Args:
            pg_port (int): Puerto de la base de datos PostgreSQL.

        Returns:
            int: Puerto local al que se ha realizado el reenvío
                de puertos SSH.
        """
        ssh_host = SSH_HOST
        ssh_username = SSH_USERNAME
        ssh_key_path = SSH_KEY_PATH
        # Crear conexión SSH
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        ssh_private_key = paramiko.RSAKey.from_private_key_file(
            ssh_key_path)
        self.ssh_client.connect(
            hostname=ssh_host,
            port=22,
            username=ssh_username,
            pkey=ssh_private_key)
        transport = self.ssh_client.get_transport()
        local_port = transport.request_port_forward("", pg_port)
        return local_port

    def execute_query(self, filename, data=None):
        """
        Ejecuta una consulta SQL desde un archivo y devuelve
            los resultados como un DataFrame.

        Args:
            filename (str): Nombre del archivo de consulta SQL
                (sin extensión).
            data (list): Lista de datos para formatear la
                consulta SQL.

        Returns:
            pd.DataFrame: DataFrame que contiene los resultados
                de la consulta.
        """
        with self.conn.cursor() as cursor:
            cursor.execute(f"SET search_path TO {DB_SCHEMA}")
            # Leer el archivo de consulta SQL
            file_route = os.path.join(ABSOLUTE_PATH, f"{filename}.sql")
            with open(file_route, 'r', encoding='utf-8') as sql_file:
                query = sql_file.read()
            # Formatear la consulta con la fecha de servicio
            if data:
                query = query.format(*data)
            # Ejecutar la consulta
            cursor.execute(query)
            # Obtener los resultados de la consulta
            results = cursor.fetchall()
            # Convertir los resultados a un DataFrame
            columns = [desc[0] for desc in cursor.description]
            df_data = pd.DataFrame(results, columns=columns)
            df_data.columns = [col.upper() for col in df_data.columns]
        return df_data
    def close(self):
        """
        Cierra la conexión SSH y la conexión a la base de datos PostgreSQL.
        """
        if self.ssh:
            self.ssh_client.close()
        self.conn.close()


if __name__ == '__main__':
    # Ejemplo de uso para la conexión a base de datos
    df = obtener_servicios('2023-04-04', '2023-06-04')
    print(df)
