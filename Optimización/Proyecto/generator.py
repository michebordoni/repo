from random import randint, shuffle
import sys
import os

# Generador de preferencias
preferencias = []

for t in range(4000):
    test = str(t + 1)
    numbers = [randint(0, 1) for i in range(4)]
    if 1 not in numbers:
        numbers[randint(0, 3)] = 1
    test += ";" + ";".join(map(str, numbers))
    preferencias.append(test)

folder_name = "./data"
# Descomentar si la carpeta no existe
# os.mkdir(folder_name)
with open(folder_name+"/preferencias.csv", "w") as pf:
    escribir = "Familia;Vivienda1;Vivienda2;Vivienda3;Vivienda4\n"+"\n".join(preferencias)
    pf.write(escribir)



# Generador de tiempos entre viviendas y familias
tiempos = []
viv1 = 14
viv2 = 28
viv3 = 49
viv4 = 63
var_viv1 = 3
var_viv2 = 7
var_viv3 = 7
var_viv4 = 7

for t in range(4000):
    test = str(t + 1)
    numbers = numbers = [
        viv1 + randint(-var_viv1, var_viv1),
        viv2 + randint(-var_viv2, var_viv2),
        viv3 + randint(-var_viv3, var_viv3),
        viv4 + randint(-var_viv4, var_viv4)
    ]
    test += ";" + ";".join(map(str, numbers))
    tiempos.append(test)

folder_name = "./data"
with open(folder_name+"/tiemposviviendas.csv", "w") as tv:
    escribir = "Familia;Vivienda1;Vivienda2;Vivienda3;Vivienda4\n"+"\n".join(tiempos)
    tv.write(escribir)



# Generador de recursos máximos en día t
# Tiempo máximo
max_tiempo = 365
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

folder_name = "./data"
with open(folder_name+"/recursos.csv", "w") as rs:
    escribir = "Tiempo;Recursos\n"+"\n".join(recursos)
    rs.write(escribir)



# Generador de cantidad de recursos y costos por tipo de vivienda
# Recursos para las viviendas en el formato [vivienda1, vivienda2, vivienda3, vivienda4]
rec_viv = [14, 16, 20, 10]
# Costos para las viviendas en el formato [vivienda1, vivienda2, vivienda3, vivienda4]
cost_viv = [3800, 4550, 22500, 40000]

info = []
for t in range(4):
    test = str(t + 1) + ";" + str(rec_viv[t]) + ";" + str(cost_viv[t])
    info.append(test)

folder_name = "./data"
with open(folder_name+"/detallesvivienda.csv", "w") as dv:
    escribir = "Vivienda;Recursos;Costos\n"+"\n".join(info)
    dv.write(escribir)