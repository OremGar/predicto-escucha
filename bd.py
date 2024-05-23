import psycopg2

def conexion():
    return psycopg2.connect(
        dsn="postgres://postgres:Aut201104@192.168.1.85/predicto"
    )