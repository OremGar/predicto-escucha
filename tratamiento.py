import calculo
import bd
import psycopg2

def TratamientoDatos(payload, devEui, date):
    temperatura = 0
    aceleraciones = {}

    roll = 0
    pitch = 0

    conexion = None
    cur = None

    try:
        temperatura = payload["Temp"]
        aceleraciones = payload["AccData"]

    except Exception as e:
        print(str(e))
        raise ValueError(e)
    
    print(temperatura)
    print(devEui)
    for elemento in aceleraciones:
        print(elemento)
        roll = calculo.CalculaRoll(xAxis=elemento["AccX"], yAxis=elemento["AccY"], zAxis=elemento["AccZ"], ultimoRoll=roll)
        pitch = calculo.CalculaPitch(xAxis=elemento["AccX"], yAxis=elemento["AccY"], zAxis=elemento["AccZ"], ultimoPitch=pitch)
    
    print(roll)
    print(pitch)

    try:
        conexion = bd.conexion()
    except Exception as e:
        print(str(e))
        raise ValueError(e)

    try:
        cur = conexion.cursor()
        cur.execute('select * from motores where eui = %(devEui)s', {"devEui":devEui})
        motores = cur.fetchall()

        for motor in motores:
            print(motor)

        cur.close()
    except psycopg2.OperationalError:
        cur.close()
        conexion.close()
        print(str(e))
        raise ValueError(e)
    


    cur.close()
    conexion.close()