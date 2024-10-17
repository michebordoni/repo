from gurobipy import Model, GRB, quicksum
import pandas as pd

# MANEJO DE DATOS ------------ RELLENAR
# -------
recursos = pd.read_csv('results/recursos.csv', sep=';')
detalle_vivienda = pd.read_csv('results/detallesvivienda.csv', sep=';')

# PARAMETROS para construcción conjunto:
cant_familias = 4
t_max = 21

# CONJUNTOS
N = [i for i in range(cant_familias)] # familias para asignar [0, cant_familias)
J = [1, 2, 3, 4] # Tipos de viviendas
T = [(t+1) for t in range(t_max)] # Horizonte de tiempo [1, t_max]

# PARAMETROS 
# - Dependientes de conjuntos

# r_t: cant max de recursos diarios disponibles
r = {row['Tiempo']: row['Recursos'] for index, row in recursos.iterrows()}

# v_j: recursos para construir vivienda tipo j
v = {row['Vivienda']: row['Recursos'] for index, row in detalle_vivienda.iterrows()}

# c_j: costo de construir vivienda j

c = {row['Vivienda']: row['Costos'] for index, row in detalle_vivienda.iterrows()}

# Q_ij: tiempo de construccion e instalacion de j 
Q = 1 # IMPORTAR EN MODEL FINAL. por ahora duracion siempre de un día

# z_ij: binaria. 1 si a familia i le sirve vivienda tipo j ( EN MODELO FINAL IMPORTAR DATO)
z = {(0, 1):1, (0, 2):0, (0, 3):0, (0, 4):0, 
    (1, 1):0, (1, 2):1, (1, 3):0, (1, 4):0, 
    (2, 1):0, (2, 2):0, (2, 3):1, (2, 4):0, 
    (3, 1):0, (3, 2):0, (3, 3):1, (3, 4):0, 
    }

# m_j: cantidad inicial de viviendas tipo j disponibles
m = {j: 300 for j in range(1, 5)}

# - Independientes de conjuntos
# S: cantidad maxima de instalaciones simultaneas
# P: presupuesto total disponible
P = 1000
M = t_max*10 # numero grande auxiliar en restriccion para definir R

model = Model() # Generar el modelo
#VARIABLES
# - binarias
x = model.addVars(N, J, T, vtype = GRB.BINARY, name="x") # vivienda j asignada a familia i el dia t
y = model.addVars(N, J, T, vtype = GRB.BINARY, name="y") # instalación de j para familia i durante dia t
# - enteras (inventario(w), cant de viviendas encargadas(u) y días totales(R) son valores enteros)
I = model.addVars(J, T, vtype = GRB.INTEGER, name="I") # inventario de viviendas disponibles tipo j al final de t
u = model.addVars(J, T, vtype = GRB.INTEGER, name="u") # viviendas tipo j que se mandan a construir en t
R = model.addVar(vtype = GRB.INTEGER, name="R") # Tiempo total para entregar viviendas a todos

model.update() # actualizar modelo

# RESTRICCIONES

# Cada familia recibe 1 sola casa en el horizonte de tiempo (SUM_{T}SUM_{J}(x) = 1 forall i)
model.addConstrs( (quicksum(x[i, j, t] for t in T for j in J) == 1 for i in N), name="R1") 

#  Cada familia solo se puede instalar en viviendas de su prioridad 
# (x_ijt 1 solo si z_ij es 1(cuando a familia i le sirve vivienda j))
model.addConstrs( ( z[(i, j)] >= quicksum(x[i, j, t] for t in T) for i in N for j in J), name="R2") 

# Instalacion comienza día que se asigna vivienda a familia y continua sin interrumpcion
# for in range no incluye el limite mayor en el dominio (por eso rangos distintos a modelo en informe)
# model.addConstrs( ( (x[i, j, t] <= y[i, j, q] for i in I for j in J for q in range[t, t+Q]) for t in range[1, t_max-Q+1] ), name="R3") 

#Asegurarse de no sobrepasar el limite de instalaciones diarias:
# model.addConstrs((quicksum(y[i, j, t] for i in range(n) for j in range(4)) <= S for t in range(T)), name="R4")

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

# FUNCION OBJETIVO
objetivo = R
model.setObjective(objetivo, GRB.MINIMIZE)
model.optimize()

# MANEJO SOLUCIONES
print("\n"+"-"*10+" RESULTADOS "+"-"*10)
print(f"Valor objetivo: {model.ObjVal}")

for i in N:
    for j in J:
        for t in T: 
            if (x[i,j,t].x > 0): # se imprime día de asignacion (valor de x mayor a 0 )
                print(f"familia {i} es asignada vivienda {j} el día {t}: x_{i},{j},{t} = {x[i,j,t].x}") 

# model.printAttr("X") # Mostrar los valores de todas las soluciones que no son 0

# Holguras (0 significa que la restricción es activa)
print("\n"+"-"*9+" Restricciones Activas "+"-"*9)
for constr in model.getConstrs():
    if constr.getAttr("slack") == 0:
        print(f"La restriccion {constr} está activa")

# Crear archivo que guarde resultados ____________________
# ____________________________

#to do
#formalizar m_j 
#como añadir tfinal para r7
#cambiar valor a P
