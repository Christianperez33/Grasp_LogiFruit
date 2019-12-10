import time
from grasp import *
import argparse
from tqdm import tqdm
import json

argparser = argparse.ArgumentParser()
argparser.add_argument('-r', '--random', help='mezcla de datos al incio del algoritmo',default=True)
argparser.add_argument('-i', '--iteraciones', help='numero de iteraciones que hace el algoritmo', default=5)
argparser.add_argument('-s', '--seed', help='semilla que utilizamos para el randomizado de los datos',default=None)
argparser.add_argument('-a', '--alfa', help='cojunto de valores que puede tomar alfa, cuan mas grande el valor mas divisiones de alfa, multiplos de 10',default=10)
argparser.add_argument('-g', '--save', help='Guarda la solución en un fichero llamado "solution_json.json"',default=False)
args = argparser.parse_args()


start_time = time.time()
sol = {}
val = None
sum_val = {}
for i in tqdm(range(int(args.iteraciones))):
    g = Grasp(args.random,args.seed)
    for alfa in range(int(args.alfa)+1):
        x = g.GRASP_Solution(alfa/int(args.alfa))
        sum_val[str(alfa/int(args.alfa))] = sum_val[str(alfa/int(args.alfa))] + x[1] if str(alfa/int(args.alfa)) in sum_val.keys() else x[1]
        if i == 0:
            sol = x[0]
            val = x[1]
        else:
            if val >= x[1]:
                sol = x[0]
                val = x[1]
                
print(len(list(sol.keys())))
if(args.save):
    with open('solution_json.json', 'w') as outfile:
        json.dump(sol, outfile)
print("---> Mejor fitness: {}".format(val))
for x in sum_val:
    print("---> Media fitness {}: {}".format(x, sum_val[x]/int(args.iteraciones)))
print("--- {} seconds ---".format(time.time() - start_time))
