"""
El Roll y Pitch son movimientos utilizados en los acelerometros para determinar el movimiento de un objeto. 
El Roll se refiere al movimiento horizontal izquierda-derecha
El Pitch al movimiento hacia adelante-atrás
"""

import sympy
import math

def CalculaRoll(xAxis, yAxis, zAxis, ultimoRoll):
    operacion = pow(xAxis, 2) + pow(zAxis, 2)
    operacion = sympy.sqrt(operacion)
    operacion = yAxis/operacion
    operacion = sympy.atan(operacion)
    operacion = operacion * 180
    operacion = operacion / math.pi

    res = (0.94 * ultimoRoll) + (0.06 * operacion) 
    return res

def CalculaPitch(xAxis, yAxis, zAxis, ultimoPitch):
    operacion = pow(yAxis, 2) + pow(zAxis, 2)
    operacion = sympy.sqrt(operacion)
    operacion = xAxis / operacion
    operacion = operacion * -1
    operacion = sympy.atan(operacion)
    operacion = operacion * 180
    operacion = operacion / math.pi

    res = (0.94 * ultimoPitch) + (0.06 * operacion) 
    return res