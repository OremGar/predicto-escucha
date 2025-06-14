import psycopg2
import os

def conexion():
    return psycopg2.connect(
        dsn = os.environ['DB_URI']
    )
