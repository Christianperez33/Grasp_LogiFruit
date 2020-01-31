import time
from grasp import *
# from prueba import *
import argparse
from tqdm import tqdm
import json

argparser = argparse.ArgumentParser()
argparser.add_argument('-r', '--random', help='mezcla de datos al incio del algoritmo', default=True)
argparser.add_argument('-i', '--iteraciones',help='numero de iteraciones que hace el algoritmo', default=5)
argparser.add_argument('-s', '--seed', help='semilla que utilizamos para el randomizado de los datos', default=None)
argparser.add_argument('-a', '--alfa', help='cojunto de valores que puede tomar alfa, cuan mas grande el valor mas divisiones de alfa, multiplos de 10', default=None)
argparser.add_argument('-av', '--a_val', help='valor de inicio de alfa', default=0.5)
argparser.add_argument('-g', '--save', help='Guarda la solución en un fichero llamado "solution_json.json"', default=False)
argparser.add_argument('-n', '--name', help='nombre del archivo que guarda la solucion"', default="solution_")
argparser.add_argument('-l', '--lcr', help='Tamaño de la lista de candidatos', default=3)
argparser.add_argument('-x', '--stock', help='Path al fichero csv de stock', default="./data/stock.csv")
argparser.add_argument('-y', '--viajes', help='Path al fichero xml de viajes', default="./data/viajes.xml",)
argparser.add_argument('-z', '--precios', help='Path al fichero csv de precios', default="./data/precios.csv")
args = argparser.parse_args()

cien = False
if int(args.a_val) > 1:
    args.a_val = int(args.a_val)/100
    cien = True
start_time = time.time()
sol = {}
val = {}
trans = {}
sum_val = {}
print("Config: Inter -> {},\n \tAlfa -> {},\n \tLCR ->{},\n \tAutosave -> {}".format(args.iteraciones,args.a_val ,args.lcr,args.save))

for i in tqdm(range(int(args.iteraciones))):
    g = Grasp(args.random, args.seed, args.stock,args.viajes,args.precios)
    if args.alfa == None:
        x = g.GRASP_Solution(float(args.a_val),int(args.lcr))
        sol[i] = x[0]
        val[i] = x[1]
        trans[i] = x[2]
        
    else:
        sol[i] = {}
        val[i] = {}
        trans[i] = {}
        for alfa in range(int(args.alfa)+1):
            x = g.GRASP_Solution(alfa/int(args.alfa),int(args.lcr),i)
            sol[i][alfa] = x[0]
            val[i][alfa] = x[1]
            trans[i][alfa] = x[2]

new_val = 0
new_sol = {}
new_trans = {}
if args.alfa == None:
    for i in val.keys():
        print("---> Iter {} fitness: {} transporte: {}".format(i,val[i],trans[i]))
        if new_val == 0:
            new_val = val[i]
            new_sol = sol[i]
            new_trans = trans[i]
        elif val[i] < new_val:
            new_val = val[i]
            new_sol = sol[i]
            new_trans = trans[i]
    val = new_val
    sol = new_sol 
    trans = new_trans
else:
    for i in val:
        for alfa in val[i]:
            print("---> Iter {} alfa {} fitness: {} transporte: {}".format(i,alfa/int(args.alfa),val[i][alfa],trans[i][alfa]))
            if new_val == 0:
                new_val = val[i][alfa]
                new_sol = sol[i][alfa]
                new_trans =  trans[i][alfa]
            elif val[i][alfa] < new_val:
                new_val = val[i][alfa]
                new_sol = sol[i][alfa]
                new_trans =  trans[i][alfa]
    val = new_val
    sol = new_sol
    trans = new_trans

if(args.save):
    with open(args.name+str(float(args.a_val)).replace(".","_")+'.json', 'w') as outfile:
        json.dump(sol, outfile)
print("---> Mejor fitness: {} Transporte: {}".format(val,trans))
print("--- {} seconds ---".format(time.time() - start_time))
