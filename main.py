import pandas as pd
from pulp import *
from tabulate import tabulate


def main():
    df = pd.read_excel("diet.xls", nrows=64)
    p = LpProblem("Dieta", LpMinimize)
    food_items = list(df['Foods'])
    weight = int(input('Enter your weight: '))
    height = int(input('Enter your height: '))
    age = int(input('Enter your age: '))
    normal_calories = 10 * weight + 6.25 * height + 5 * age - 161
    ans = int(input('1. sedentary work\n2. sedentary plus light sports up to three times a week \n3. physical'
                           ' labor up to 12 hours without heavy loads\n4. sedentary work and sports more than three'
                           ' times a week\n5. physical labor and intensive sports\n6. sedentary work and sports 5'
                           ' days a week\n7. physical labor up to 12 hours plus intensive sports 5 times a'
                           ' week\n8. housewives'))
    if ans == 1:
        activ = 1.2
    elif ans == 2 or ans == 8:
        activ = 1.3
    elif ans == 3:
        activ = 1.5
    elif ans == 4:
        activ = 1.4
    elif ans == 5 or ans == 6:
        activ = 1.6
    elif ans == 7:
        activ = 1.9
    else:
        activ = 1.3
    normal_calories = (normal_calories * activ) * 0.9
    normal = {}
    normal['carbs'] = normal_calories * 0.5 / 4
    normal['protein'] = normal_calories * 0.3 / 4
    normal['fat'] = normal_calories * 0.2 / 9
    normal['calories'] = normal_calories
    creating_d(food_items, df, p, normal)


def creating_d(food, tble, prob, normal_d):
    costs = dict(zip(food, tble['Price/ Serving']))
    calories = dict(zip(food, tble['Calories']))
    fat = dict(zip(food, tble['Total_Fat g']))
    carbs = dict(zip(food, tble['Carbohydrates g']))
    protein = dict(zip(food, tble['Protein g']))
    portions = dict(zip(food, tble['Serving Size g']))

    sodium = dict(zip(food, tble['Sodium mg']))
    fiber = dict(zip(food, tble['Dietary_Fiber g']))
    calcium = dict(zip(food, tble['Calcium mg']))
    iron = dict(zip(food, tble['Iron mg']))
    cholesterol = dict(zip(food, tble['Cholesterol mg']))

    food_vars = LpVariable.dicts("*", food, 0, cat='Continuous')
    prob += lpSum([costs[i] * food_vars[i] for i in food])
    minmax(prob, calories, food_vars, food, fat, carbs, protein, normal_d, sodium, fiber, calcium, iron,
           cholesterol, portions)


def minmax(p, calories, food_vars, food_items, fat, carbs, protein, normal_d, sodium, fiber, calcium, iron,
           cholesterol, portions):
    # Calorie
    p += lpSum([calories[f] * food_vars[f] for f in food_items]) >= 1000.0  # CalorieMinimum
    p += lpSum([calories[f] * food_vars[f] for f in food_items]) <= int(normal_d['calories'])  # CalorieMaximum
    # Fat
    p += lpSum([fat[f] * food_vars[f] for f in food_items]) >= 20.0
    p += lpSum([fat[f] * food_vars[f] for f in food_items]) <= int(normal_d['fat'])
    # Carbs
    p += lpSum([carbs[f] * food_vars[f] for f in food_items]) >= 100.0
    p += lpSum([carbs[f] * food_vars[f] for f in food_items]) <= int(normal_d['carbs'])
    # Protein
    p += lpSum([protein[f] * food_vars[f] for f in food_items]) >= 60.0
    p += lpSum([protein[f] * food_vars[f] for f in food_items]) <= int(normal_d['protein'])
    # Sodium
    p += lpSum([sodium[f] * food_vars[f] for f in food_items]) >= 800.0
    p += lpSum([sodium[f] * food_vars[f] for f in food_items]) <= 2000.0
    # Cholesterol
    p += lpSum([cholesterol[f] * food_vars[f] for f in food_items]) >= 30.0
    p += lpSum([cholesterol[f] * food_vars[f] for f in food_items]) <= 240.0
    # Fiber
    p += lpSum([fiber[f] * food_vars[f] for f in food_items]) >= 125.0
    p += lpSum([fiber[f] * food_vars[f] for f in food_items]) <= 250.0
    # Calcium
    p += lpSum([calcium[f] * food_vars[f] for f in food_items]) >= 700.0
    p += lpSum([calcium[f] * food_vars[f] for f in food_items]) <= 1500.0
    # Iron
    p += lpSum([iron[f] * food_vars[f] for f in food_items]) >= 10.0
    p += lpSum([iron[f] * food_vars[f] for f in food_items]) <= 40.0

    # p.writeLP("SimpleDietProblem.lp")
    p.solve()
    print('Your Diet for Safe Weight Loss (least cost): ')
    print(tabulate(normal_d.items(), headers=['ELEMENT', 'VALUE G.'], tablefmt="grid"))
    print("-" * 110)
    new_dicts_food_var = {v: k for k, v in food_vars.items()}
    for v in p.variables():
        if v.varValue > 0:
            print(str(v.name)[2:], "=", v.varValue, 'or', portions[new_dicts_food_var[v]] * v.varValue, 'g.')
    print("The total cost of this balanced diet is: ${}".format(round(value(p.objective), 2)))


main()
