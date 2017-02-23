# -*- coding: utf-8 -*-
import MySQLdb
import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt

# para una sola estación
Estacion = 99

# Variables iniciales
fec_ini = '2016-12-21'
fec_fin = '2016-12-21'
hora_ini = '04:00:00'
hora_fin = '05:10:00'

# para nivel se debe hacer una consulta preliminar para determinar el tipo de estación,
# N esta en la tabla estaciones, si N = 0 trabaja con Pr y si N= 1 se trabaja con Ni
# Nivel = offset - (Pr ó Ni)

'''
En la tabla estaciones estan los campos N y N2, si N = 0 entonces N2 = 1 y si N2 = 0 entonces N = 1 en alguna estación
Es decir N y N2 pueden ser cero o uno.
esto es para saber la forma de calcular el nivel así:
N  = 1: -1*(Ni - offsetN)
N2 = 1: -1*(Pr - offsetN)
'''

'''
Para hacer la consulta de nivel se puede hacer en dos consultas
primero a la tabla estaciones y luego a la tabla datos.

SELECT offsetN, N, codigo FROM estaciones WHERE codigo = 99;
el offsetN de esta consulta es 1282, la estacion 99 tiene N = 1
SELECT cliente, fecha, hora, (NI-1282)*-1 FROM datos WHERE cliente=99 AND fecha BETWEEN '2016-12-21' AND '2016-12-22';
'''


def ejecutar_consulta_sql(sentencia, host, usuario, clave, bd):
    """
    Esta función toma una sentencia sql y devuelve una tupa con los registros.
    """
    db = MySQLdb.connect(host=host, user=usuario, passwd=clave, db=bd);
    cursor = db.cursor()
    cursor.execute(sentencia)
    nivel_ = cursor.fetchall()
    # Cerrar el cursor
    cursor.close()
    # Cerrar la conexión
    db.close()
    return nivel_


# consulta para saber el tipo de estacion si funciona con Pr ó Ni y el offset de la estación.
sentencia_tipo = "SELECT offsetN, N, N2, codigo FROM estaciones WHERE codigo = " + str(Estacion) + ";"
tipo = ejecutar_consulta_sql(sentencia_tipo)
# tipo es una tupla de tuplas, para verificarlo hacer print tipo.
offsetn = tipo[0][0]
N = tipo[0][1]

print('offsetN:' + str(offsetn))
print('N:' + str(N))

# se ejecuta la consulta de nivel usando el offsetN de la estacion.
sentencia_nivel = "SELECT cliente, fecha, hora, DATE_FORMAT(CONCAT(fecha, ' ', hora), '%Y-%m-%d %H:%i:%s') " \
                  "as fecha_completa,(NI - {} )*-1 FROM datos WHERE " \
                  "cliente = {} AND fecha BETWEEN '2016-12-21' AND '2016-12-22';".format(str(offsetn), str(Estacion))

# se ejecuta la sentencia de nivel y se guarda la tupla de tuplas en un variable que llamamos resultado.
resultado = ejecutar_consulta_sql(sentencia_nivel)
print(type(resultado))

# Pasar la tupla (que es una tupla de tuplas) a una lista

# Se crean listas vacias, una por cada columna de la tabla
# luego se recorre la tupla y se van llenando las listas correspondientes.
cliente = []
fecha = []
hora = []
fecha_completa = []
nivel = []

for i in range(len(resultado)):
    cliente.append(resultado[i][0])
    fecha.append(resultado[i][1])
    hora.append(resultado[i][2])
    fecha_completa.append(resultado[i][3])
    nivel.append(resultado[i][4])

# Para crear el DataFrame primero se crea un diccionario

diccionario = {'cliente': cliente, 'fecha': fecha_completa, 'nivel': nivel}
dataframe = pd.DataFrame(diccionario)
print(dataframe)

dataframe['fecha'] = pd.to_datetime(dataframe['fecha'])
fechas = dataframe['fecha'].values

# Para graficar
fig = plt.figure(figsize=[15, 10])
ax = fig.add_subplot(111)
ax.plot(fechas, nivel, label='Resultado')
ax.set_xlabel("Hora", fontsize=24)
ax.set_ylabel("Nivel", fontsize=24)
ax.set_title(u"Nivel", fontsize=30)
ax.grid(True)
ax.legend()
plt.show()
