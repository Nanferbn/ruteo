from decouple import config

# Cargar las variables de entorno desde el archivo .env
DEBUG = config('DEBUG', cast=bool)
PROD_DATA = config('PROD_DATA', cast=bool)
DB_NAME = config('DB_NAME_TEST') if DEBUG else config('DB_NAME')
DB_USER = config('DB_USER_TEST') if DEBUG else config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD_TEST') if DEBUG else config('DB_PASSWORD')
DB_HOST = config('DB_HOST_TEST') if DEBUG else config('DB_HOST')
DB_PORT = config('DB_PORT_TEST') if DEBUG else config('DB_PORT')
DB_SCHEMA = config('DB_SCHEMA_TEST') if DEBUG else config('DB_SCHEMA')
GOOGLE_KEY = config('GOOGLE_KEY')
SSH_HOST = config('SSH_HOST')
SSH_USERNAME = config('SSH_USERNAME')
SSH_KEY_PATH = config('SSH_KEY_PATH')
ABSOLUTE_PATH = config('ABSOLUTE_PATH')
