import calculo
import bd
import psycopg2
import conversion
import datetime
import firebase
import pandas as pd
import requests

TIPO_ANOMALIA_ROLL = "roll"
TIPO_ANOMALIA_PITCH = "pitch"
TIPO_ANOMALIA_TEMPERATURA = "temperatura"

def TratamientoDatos(payload, devEui, fechaStr):
    temperatura = 0
    aceleraciones = {}
    aceleracionesX = []
    aceleracionesY = []
    aceleracionesZ = []

    difX = 0
    difY = 0
    difZ = 0

    esPrimero = False

    aceleraciones = ()

    ultimoEstadoContador = 0
    vibracionesContador = 0

    roll = 0
    pitch = 0

    tolerancias = None
    tolerancia = None

    motores = None
    motor = None

    motoresVibraciones = None

    usuarios = None
    usuariosTokens = []

    idGravitacion = None

    conexion = None
    cur = None

    try:
        conexion = bd.conexion()
    except Exception as e:
        print(str(e))
        raise ValueError(e)

    #Se obtiene el motor
    try:
        cur = conexion.cursor()
        cur.execute('select * from motores where eui = %(devEui)s', {"devEui":devEui})
        motores = cur.fetchall()
        
        if len(motores) == 0:
            return

        motor = motores[0]

        cur.close()
        conexion.commit()
    except psycopg2.OperationalError:
        cur.close()
        conexion.close()
        print(str(e))
        raise ValueError(e)

    #Se cuentan las vibraciones, si es menor a 0, se hace el ajuste inicial COMPLETARRRRR
    try:
        cur = conexion.cursor()
        cur.execute('select count(*) > 0 from motores_vibraciones where id_motor = %(motor)s', {"motor":motor[0]})
        motorVibCont = cur.fetchone()[0]
        esPrimero = motorVibCont

    except Exception as e:
        print(str(e))
        raise ValueError(e)

    #Se obtiene la temperatura y las aceleraciones del payload
    try:
        temperatura = payload["Temp"]
        aceleraciones = payload["AccData"]

    except Exception as e:
        print(str(e))
        raise ValueError(e)
    
    fechaStrTruncated = fechaStr[:19]

    # Convertir la cadena truncada a un objeto datetime
    fecha = datetime.datetime.strptime(fechaStrTruncated, "%Y-%m-%dT%H:%M:%S")
    fecha = fecha - datetime.timedelta(hours=6)

    #Se agregan las aceleraciones a la base de datos
    for elemento in aceleraciones:
        aceleracionesX.append(elemento["AccX"])
        aceleracionesY.append(elemento["AccY"])
        aceleracionesZ.append(elemento["AccZ"])
        try:
            cur = conexion.cursor()
            cur.execute("insert into aceleraciones (id_motor, fecha, eje_x, eje_y, eje_z) values (%(motor)s,%(fecha)s,%(eje_x)s,%(eje_y)s,%(eje_z)s)", {"motor":motor[0], "fecha":fecha, "eje_x":elemento["AccX"], "eje_y":elemento["AccY"], "eje_z":elemento["AccZ"]})
            conexion.commit()
            cur.close()
        except Exception as e:
            cur.close()
            conexion.close
            print(str(e))
            raise ValueError(e)

    # Se calcula el roll y pitch de las aceleraciones para después ser agregadas
    for i,_ in enumerate(aceleracionesX):
        roll = calculo.CalculaRoll(xAxis=aceleracionesX[i], yAxis=aceleracionesY[i], zAxis=aceleracionesZ[i], ultimoRoll=roll)
        pitch = calculo.CalculaPitch(xAxis=aceleracionesX[i], yAxis=aceleracionesY[i], zAxis=aceleracionesZ[i], ultimoPitch=pitch)

    try:
        cur = conexion.cursor()
        cur.execute("insert into gravitacion (id_motor, roll, pitch, fecha, temperatura) values (%(motor)s,%(roll)s,%(pitch)s,%(fecha)s,%(temperatura)s) returning id", {"motor":motor[0], "roll":float(roll), "pitch":float(pitch), "fecha":fecha, "temperatura":float(temperatura)})
        idGravitacion = cur.fetchone()[0]
        conexion.commit()
        cur.close()
    except Exception as e:
        cur.close()
        conexion.close()
        print(str(e))
        raise ValueError(e)
    
    #Se convierten las aceleraciones en coordenadas
    vibracionesX, vibracionesY, vibracionesZ = conversion.AcelACoor(aceleracionesX, aceleracionesY, aceleracionesZ)

    #Se agregan las coordenadas (vibraciones) a la base de datos
    for i,_ in enumerate(vibracionesX):

        try:
            cur = conexion.cursor()
            cur.execute("insert into motores_vibraciones (hora, eje_x, eje_y, eje_z, id_motor) values (%(hora)s,%(eje_x)s,%(eje_y)s,%(eje_z)s,%(id_motor)s)", {"hora":fecha, "eje_x":float(vibracionesX[i]), "eje_y":float(vibracionesY[i]), "eje_z":float(vibracionesZ[i]), "id_motor":motor[0]})
            conexion.commit()
            cur.close()
        except Exception as e:
            cur.close()
            conexion.close()
            print(str(e))
            raise ValueError(e)

    #Se obtiene el conteo de vibraciones actual
    try:
        cur = conexion.cursor()
        cur.execute('select count(*) from motores_vibraciones where id_motor = %(motor)s', {"motor":motor[0]})
        vibracionesContador = cur.fetchone()[0]
        
        conexion.commit()
        cur.close()
    except Exception as e:
        print(str(e))
        raise ValueError(e)

    #Se obtienen los tokens de los dispositivos de firebase
    try:
        cur = conexion.cursor()
        cur.execute("select * from token_firebase")
        usuarios = cur.fetchall()

        cur.close()
        conexion.commit()
    except Exception as e:
        cur.close()
        conexion.close()
        print(str(e))
        raise ValueError(e)

    #Se agregan a la lista de usuariosTokens los tokens de los usuarios
    for usuario in usuarios:
        usuariosTokens.append(usuario[0])


    try:
        cur = conexion.cursor()
        cur.execute("select * from tolerancia where id_motor = %(motor)s", {"motor":motor[0]})
        tolerancias = cur.fetchall()
        tolerancia = tolerancias[0]

        cur.close()
        conexion.commit()
    except Exception as e:
        cur.close()
        conexion.close()
        print(str(e))
        raise ValueError(e)

    if roll > tolerancia[2] or roll < tolerancia[3]:
        try:
            firebase.EnviaNotificacion(cuerpo="Se detecto una desviación horizontal anomala", destinos=usuariosTokens, titulo=f"Motor {motor[0]}")
        except Exception as e:
            print(str(e))
            raise ValueError(e)

        try:
            cur = conexion.cursor()
            cur.execute("insert into anomalias (id_gravitacion, anomalia) values (%(id_gravitacion)s, %(anomalia)s)", {"id_gravitacion":idGravitacion, "anomalia":TIPO_ANOMALIA_ROLL})
            conexion.commit()
            cur.close()
        except Exception as e:
            cur.close()
            conexion.close()
            print(str(e))
            raise ValueError(e)

    if pitch > tolerancia[5] or pitch < tolerancia[6]:
        try:
            firebase.EnviaNotificacion(cuerpo="Se detecto una desviación vertical anomala", destinos=usuariosTokens, titulo=f"Motor {motor[0]}")
        except Exception as e:
            print(str(e))
            raise ValueError(e)

        try:
            cur = conexion.cursor()
            cur.execute("insert into anomalias (id_gravitacion, anomalia) values (%(id_gravitacion)s, %(anomalia)s)", {"id_gravitacion":idGravitacion, "anomalia":TIPO_ANOMALIA_PITCH})
            conexion.commit()
            cur.close()
        except Exception as e:
            cur.close()
            conexion.close()
            print(str(e))
            raise ValueError(e)

    if temperatura > tolerancia[4]:
        try:
            firebase.EnviaNotificacion(cuerpo="Se detecto una temperatura anomala", destinos=usuariosTokens, titulo=f"Motor {motor[0]}")
        except Exception as e:
            print(str(e))
            raise ValueError(e)
        
        try:
            cur = conexion.cursor()
            cur.execute("insert into anomalias (id_gravitacion, anomalia) values (%(id_gravitacion)s, %(anomalia)s)", {"id_gravitacion":idGravitacion, "anomalia":TIPO_ANOMALIA_TEMPERATURA})
            conexion.commit()
            cur.close()
        except Exception as e:
            cur.close()
            conexion.close()
            print(str(e))
            raise ValueError(e)
    
    #Se cuentan los estados del motor
    try:
        cur = conexion.cursor()
        cur.execute("select count(*) from motores_estados where id_motor = %(id_motor)s", {"id_motor":motor[0]})
        
        if cur.fetchone()[0] > 0:
            conexion.commit()
            cur.close()
            
            cur = conexion.cursor()
            
            cur.execute("select contador from motores_estados where id_motor = %(id_motor)s order by fecha DESC LIMIT 1", {"id_motor":motor[0]})
            ultimoEstadoContador = cur.fetchone()[0]
            
            conexion.commit()
            cur.close()

        conexion.commit()
        cur.close()
    except Exception as e:
        cur.close()
        conexion.close()
        print(str(e))
        raise ValueError(e)

    if ultimoEstadoContador == 0 or (ultimoEstadoContador + 100) < vibracionesContador:
        try:
            cur = conexion.cursor()
            cur.execute("select eje_x, eje_y from motores_vibraciones where id_motor = %(id_motor)s ORDER BY hora DESC", {"id_motor":motor[0]})
            motoresVibraciones = cur.fetchall()
            df = pd.DataFrame(motoresVibraciones)
            data = df.values.tolist()

            respuesta = requests.post("http://172.18.0.24:8000/receive_dataframe", json={"data": data})
            if respuesta.json()["exito"] == True:
                conexion.commit()
                cur.close()

                cur = conexion.cursor()
                cur.execute("insert into motores_estados (id_motor, fecha, estado, contador) values(%(id_motor)s, %(fecha)s, %(estado)s, %(contador)s)", {"id_motor":motor[0], "fecha":fecha, "estado":respuesta.json()["cuerpo"], "contador":vibracionesContador})

            conexion.commit()
            cur.close()
        except Exception as e:
            cur.close()
            conexion.close()
            print(str(e))
            raise ValueError(e)

    print(temperatura)
    print(pitch)
    print(roll)

    print(aceleraciones)

    cur.close()
    conexion.close()