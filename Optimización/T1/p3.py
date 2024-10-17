from gurobipy import Model, GRB, GurobiError

# nombre del modelo 
model = Model("p3")

# restricciones del dominio de x1 y x2 
x1 = model.addVar(lb=0, name="x1") 
x2 = model.addVar(lb=0, name="x2") 

# especifica la función objetivo
model.setObjective(x1 + x2, GRB.MAXIMIZE)

# añade las restricciones
model.addConstr(15 * x1 + 12 * x2 <= 97, "c1")
model.addConstr(16 * x1 + 10 * x2 <= 100, "c2")
model.addConstr(2 * x1 + 8 * x2 <= 43, "c3")
model.addConstr(x2 <= 5, "c4")
model.addConstr(2 * x1 + 3 * x2 >= 8, "c5")

# optimiza el modelo
model.optimize()

# imprime los resultados
print(f'Solución optima: {model.objVal}')
print(f'Valor x1: {x1.X}')
print(f'Valor x2: {x2.X}')