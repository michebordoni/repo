from gurobipy import Model, GRB, quicksum
import pandas as pd
import csv

# ------- MANEJO DE DATOS ------------
recursos = pd.read_csv('results/recursos.csv', sep=';')
detalle_vivienda = pd.read_csv('results/detallesvivienda.csv', sep=';')
preferencias = pd.read_csv('results/preferencias.csv', sep=';')
tiempos_viviendas = pd.read_csv('results/tiemposviviendas.csv', sep=';')
# PARAMETROS para construcción conjunto:

cant_familias = 50
t_max = 365

# CONJUNTOS
N = [i for i in range(1, cant_familias + 1)] # familias para asignar [0, cant_familias]
J = [1, 2, 3, 4] # Tipos de viviendas
T = [(t + 1) for t in range(t_max)] # Horizonte de tiempo [1, t_max]

# PARAMETROS 
# - Dependientes de conjuntos

# r_t: cant max de recursos diarios disponibles
r = {row['Tiempo']: row['Recursos'] for index, row in recursos.iterrows()}
# v_j: recursos para construir vivienda tipo j
v = {row['Vivienda']: row['Recursos'] for index, row in detalle_vivienda.iterrows()}
# c_j: costo de construir vivienda j
c = {row['Vivienda']: row['Costos'] for index, row in detalle_vivienda.iterrows()}

# Q_ij: tiempo de construccion e instalacion de j 
q = dict()
for index, row in tiempos_viviendas.iterrows():
    for j in range(1, 5):  # Vivienda 1 a 4
        q[(row['Familia'], j)] = row[f'Vivienda{j}']



# z_ij: binaria. 1 si a familia i le sirve vivienda tipo j ( EN MODELO FINAL IMPORTAR DATO)
z = dict()
for index, row in preferencias.iterrows():
    i = int(row['Familia'])
    z[(i, 1)] = int(row['Vivienda1'])
    z[(i, 2)] = int(row['Vivienda2'])
    z[(i, 3)] = int(row['Vivienda3'])
    z[(i, 4)] = int(row['Vivienda4'])
          
# m_j: cantidad inicial de viviendas tipo j disponibles
m = {j: 12 if j == 1 else 0 for j in range(1, 5)}

# - Independientes de conjuntos
S = 20 # S: cantidad maxima de instalaciones simultaneas
P = 326100000 # P: presupuesto total disponible
M = t_max * 1000 # numero grande auxiliar en restriccion para definir R

model = Model() # Generar el modelo


#VARIABLES
# - binarias
x = model.addVars(N, J, T, vtype = GRB.BINARY, name="x") # vivienda j asignada a familia i el dia t
y = model.addVars(N, J, T, vtype = GRB.BINARY, name="y") # instalación de j para familia i durante dia t
# - enteras (inventario(I), cant de viviendas encargadas(u) y días totales(R) son valores enteros)
I = model.addVars(J, T, vtype = GRB.INTEGER, name="I") # inventario de viviendas disponibles tipo j al final de t
u = model.addVars(J, T, vtype = GRB.INTEGER, name="u") # viviendas tipo j que se mandan a construir en t
R = model.addVar(vtype = GRB.INTEGER, name="R") # Tiempo total para entregar vivienda a cada familia

model.update() # actualizar modelo

# RESTRICCIONES

# Cada familia recibe 1 sola casa en el horizonte de tiempo (SUM_{T}SUM_{J}(x) = 1 forall i)
model.addConstrs( (quicksum(x[i, j, t] for t in T for j in J) == 1 for i in N), name="R1") 

#  Cada familia solo se puede instalar en viviendas de su prioridad 
# (x_ijt 1 solo si z_ij es 1(cuando a familia i le sirve vivienda j))
model.addConstrs( ( z[(i, j)] >= quicksum(x[i, j, t] for t in T) for i in N for j in J), name="R2") 

# Tiempo maximo de instalación de una vivienda y que no debe existir instalación si vivienda no ha sido asignada
model.addConstrs( ( quicksum(y[i, j, t] for t in T) == (quicksum(x[i, j, t] for t in T) * q[(i, j)]) for i in N for j in J), name="R2.1")

# Instalacion comienza día que se asigna vivienda a familia y continua sin interrupción
model.addConstrs( ( x[i, j, t] <= y[i, j, t_p] for t in range(1, T[-1] - q[(i,j)]) for i in N for j in J for t_p in range(t, t + q[(i, j)] - 1) if t_p < 366), name="R3")

# Asegurarse de no sobrepasar el limite de instalaciones diarias:
model.addConstrs((quicksum(y[i, j, t] for i in N for j in J) <= S for t in T), name="R4")

#Inventario inicial de viviendas por tipo:
model.addConstrs( ( I[j, 1] == m[j] + u[j, 1] - quicksum(x[i, j, 1] for i in N) for j in J), "R5")

#Inventario de viviendas por tipo:
model.addConstrs( ( I[j, t] == I[j, t-1] + u[j, t] - quicksum(x[i, j, t] for i in N) for j in J for t in range(2, len(T))), "R6")

#El inventario al final del ´ultimo periodo debe estar vacio:
model.addConstr(quicksum(I[j, T[-1]] for j in J) == 0, "R7")

#Limite de produccion de viviendas diarias dado los recursos disponibles:
model.addConstrs( (quicksum(v[j]*u[j, t] for j in J) <= r[t] for t in T), "R8" )

#Limite de produccion total de viviendas en el tiempo dado un presupuesto maximo P
model.addConstr((quicksum(quicksum(c[j]*u[j, t] for j in J) for t in T) <= P), "R9" )

#Definicion de R(tiempo total) mayor o igual a ultimo día de última instalación
model.addConstrs( (R >= t - M*(1- y[i, j, t]) for i in N for j in J for t in T), name="RFinal")

#Restricción extra para que el modelo indique soluciones lógicas
model.addConstrs( (R >= t - M*(1- x[i, j, t]) for i in N for j in J for t in T), name="RFinal2") 

# Definicón de no negatividad para inventario y producción de viviendas
model.addConstrs( (I[j, t] >= 0 for j in J for t in T), "RN1")
model.addConstrs( (u[j, t] >= 0 for j in J for t in T), "RN2")

# FUNCION OBJETIVO
objetivo = R
model.setObjective(objetivo, GRB.MINIMIZE)
model.optimize()

# MANEJO SOLUCIONES
print("\n"+"-"*20+" RESULTADOS "+"-"*20)
print(f"Valor objetivo: {model.ObjVal}")

print("Detalles de la solución:")
print("-"*50)
no_activity_start = -1
no_activity_final = -1
for t in T:
    tr1 = 0
    tr2 = 0
    transacciones = [u[1,t].x, u[2,t].x, u[3,t].x, u[4,t].x]
    familias = []
    for j in J:
        for i in N:
            if x[i, j, t].x > 0:
                familias.append([i, j])
            if x[i, j, t].x > 0:
                tr1 += 1
            if y[i, j, t].x > 0:
                tr2 += 1
    tr1 += sum(transacciones)
    if tr1 + tr2 == 0:
        break
    elif tr1 == 0 and tr2 > 0:
        if no_activity_start == -1:
            no_activity_start = t
        elif no_activity_start != -1:
            no_activity_final = t
    else:
        if no_activity_final != -1:
            print(f"Días {no_activity_start} - {no_activity_final} sin nueva información, solo construcciones")
            no_activity_start = -1
            no_activity_final = -1
            print("-"*50)
        elif no_activity_start != -1:
            print(f"Día {no_activity_start} sin nueva información, solo construcciones")
            no_activity_start = -1
            no_activity_final = -1
            print("-"*50)
        if tr1 > 0:
            print(f"Día {t}")
            print("\tViviendas transadas por tipo:")
            if u[1,t].x > 0:
                print(f"\t\tVivienda 1: {u[1,t].x}")
            if u[2,t].x > 0:
                print(f"\t\tVivienda 2: {u[2,t].x}")
            if u[3,t].x > 0:
                print(f"\t\tVivienda 3: {u[3,t].x}")
            if u[4,t].x > 0:
                print(f"\t\tVivienda 4: {u[4,t].x}")
            if u[1,t].x + u[2,t].x + u[3,t].x + u[4,t].x <= 0:
                print(f"\t\tNo se compran viviendas en el día {t}")
            print("\tInventario de viviendas por tipo:")
            if I[1,t].x > 0:
                print(f"\t\tVivienda 1: {I[1,t].x}")
            if I[2,t].x > 0:
                print(f"\t\tVivienda 2: {I[2,t].x}")
            if I[3,t].x > 0:
                print(f"\t\tVivienda 3: {I[3,t].x}")
            if I[4,t].x > 0:
                print(f"\t\tVivienda 4: {I[4,t].x}")
            print(f"\tInfo familias:")
            for info in familias:
                print(f"\t\tFamilia {info[0]} es asignada vivienda {info[1]}")
            if len(familias) == 0:
                print("\tSe están realizando construcciones, sin información nueva que reportar")
            print("-"*50)
print("\n")
print("-"*50)
print("El resto de días no hay actividad, todas las familias tienen vivienda")


# print("___familia, vivienda, día___")
# solucion_asignacion = [] # lista para guardar solucion sobre asignacion (familia, tipo_vivienda, día)
# for i in N:
#     for j in J:
#         for t in T: 
#             if (x[i,j,t].x > 0): # se imprime día de asignacion (valor de x mayor a 0 )
#                 print(f"familia {i} es asignada vivienda {j} el día {t}: x_{i},{j},{t} = {x[i,j,t].x}") 
#                 fila = [i, j, t]
#                 solucion_asignacion.append(fila)
#                 print(fila)

# print("vivenda y cantidad mandada a hacer cada día") # para primeros 10 dias
# titulo = "| tipo_vivienda" # 15 caracteres
# for t in T: # for t in T para incluir todos
#     titulo += f" |  {t} "
# print(titulo)
# for j in J:
#     texto = f"|       {j}       |"
#     for t in T:
#         texto += f" {quicksum(x[i, j, t].x for i in N)} |"
#     print(texto)
### IDEA FUNCIONA: HACER EN EXCEL


#solucion_pedidos = []
#for j in J:
#    fila = []
#    for t in T: 
#        fila.append(u[j, t].x)
#        solucion_pedidos.append(fila)
#        print(fila)

# _______________________________________________________
# model.printAttr("X") # Mostrar los valores de todas las soluciones que no son 0

# Holguras (0 significa que la restricción es activa)
#print("\n"+"-"*9+" Restricciones Activas "+"-"*9)
#for constr in model.getConstrs():
#    if constr.getAttr("slack") == 0:
#        print(f"La restriccion {constr} está activa")

# Crear archivo que guarde resultados ____________________
# ____________________________
#from pandas import ExcelWriter
#def excel_soluciones():
#    datos = pd.DataFrame(solucion_asignacion, columns = ["familias", "vivienda", "día"])
#    archivo = ExcelWriter("solucion/asignacion_viviendas.xlsx") 
#    datos.to_excel(archivo, "solucion asignacion", index = False)
#    archivo.save()
    
