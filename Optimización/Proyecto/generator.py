from random import randint, shuffle
import sys
import os

folder_name = "results"

# Generador de preferencias
preferencias = []
for i in range(4000):
    test = str(i)
    numbers = [randint(0, 1) for i in range(4)]
    if 1 not in numbers:
        numbers[randint(0, 3)] = 1
    test += ";" + ";".join(map(str, numbers))
    preferencias.append(test)

# Descomentar si la carpeta no existe
# os.mkdir(folder_name)
with open(folder_name+"/preferencias.csv", "w") as pf:
    escribir = "Familia;Vivienda1;Vivienda2;Vivienda3;Vivienda4\n"+"\n".join(preferencias)
    pf.write(escribir)



# Generador de tiempos entre viviendas y familias
# Vivienda 1: ESCRIBIR -> tiempo promedio de construcción XX días (variación de 4 días)
# Vivienda 2: ESCRIBIR -> tiempo promedio de construcción XX días (variación de 3 días)
# Vivienda 3: ESCRIBIR -> tiempo promedio de construcción XX días (variación de 5 días)
# Vivienda 4: ESCRIBIR -> tiempo promedio de construcción XX días (variación de 3 días)
tiempos = []
# Cambiar si es necesario o para testing
viv1 = 15
viv2 = 10
viv3 = 23
viv4 = 14
var_viv1 = 4
var_viv2 = 3
var_viv3 = 5
var_viv4 = 3

for i in range(4000):
    test = str(i)
    numbers = numbers = [
        viv1 + randint(-var_viv1, var_viv1),
        viv2 + randint(-var_viv2, var_viv2),
        viv3 + randint(-var_viv3, var_viv3),
        viv4 + randint(-var_viv4, var_viv4)
    ]
    test += ";" + ";".join(map(str, numbers))
    tiempos.append(test)

with open(folder_name+"/tiemposviviendas.csv", "w") as tv:
    escribir = "Familia;Vivienda1;Vivienda2;Vivienda3;Vivienda4\n"+"\n".join(tiempos)
    tv.write(escribir)


# Generador de recursos máximos en día t
# Tiempo máximo
max_tiempo = 90
recursos = []
# Promedio de recursos
mean = 200
# Variación de recursos
var_rec = 15

for t in range(max_tiempo):
    test = str(t + 1)
    numbers = str(mean + randint(-var_rec, var_rec))
    test += ";" + numbers
    recursos.append(test)

with open(folder_name+"/recursos.csv", "w") as rs:
    escribir = "Tiempo;Recursos\n"+"\n".join(recursos)
    rs.write(escribir)


# Generador de cantidad de recursos y costos por tipo de vivienda
# Cambiar de ser necesario o para testing
# Recursos para las viviendas en el formato [vivienda1, vivienda2, vivienda3, vivienda4]
rec_viv = [14, 16, 20, 10]
# Costos para las viviendas en el formato [vivienda1, vivienda2, vivienda3, vivienda4]
cost_viv = [500, 1000, 780, 800]

info = []
for t in range(4):
    test = str(t + 1) + ";" + str(rec_viv[t]) + ";" + str(cost_viv[t])
    info.append(test)

with open(folder_name+"/detallesvivienda.csv", "w") as dv:
    escribir = "Vivienda;Recursos;Costos\n"+"\n".join(info)
    dv.write(escribir)