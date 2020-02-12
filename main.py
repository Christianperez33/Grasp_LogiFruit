import time
from grasp import *
import argparse
from tqdm import tqdm
import json

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

argparser = argparse.ArgumentParser()
argparser.add_argument('-r', '--random', help='mezcla de datos al incio del algoritmo', default=True)
argparser.add_argument('-i', '--iteraciones',help='numero de iteraciones que hace el algoritmo', default=5)
argparser.add_argument('-s', '--seed', help='semilla que utilizamos para el randomizado de los datos', default=None)
argparser.add_argument('-av', '--a_val', help='valor de inicio de alfa', default=0.5)
argparser.add_argument('-g', '--save', help='Guarda la solución en un fichero llamado "solution_json.json"', default=False)
argparser.add_argument('-n', '--name', help='nombre del archivo que guarda la solucion"', default="solution_")
argparser.add_argument('-l', '--lcr', help='Tamaño de la lista de candidatos', default=3)
argparser.add_argument('-x', '--stock', help='Path al fichero csv de stock', default="./data/stock.csv")
argparser.add_argument('-y', '--viajes', help='Path al fichero xml de viajes', default="./data/viajes.xml",)
argparser.add_argument('-z', '--precios', help='Path al fichero csv de precios', default="./data/precios.csv")
argparser.add_argument('-d', '--debug', help='Muestra por pantalla los resultados de las diferentes ejecuciones', default=True ,type=str2bool)
argparser.add_argument('-t', '--test', help='Modo hard para testeo de todos los tipos de valores', default=False ,type=str2bool)
args = argparser.parse_args()
cien = False

old_aval = args.a_val
if int(args.a_val) > 1:
    args.a_val = int(args.a_val)/100
    cien = True
start_time = time.time()
sol = {}
val = {}
trans = {}
sum_val = {}

if args.debug:
    print("Config: Inter -> {},\n \tAlfa -> {},\n \tLCR ->{},\n \tAutosave -> {}".format(args.iteraciones,args.a_val ,args.lcr,args.save))
    

for i in tqdm(range(int(args.iteraciones)),disable=(not args.debug)):
    g = Grasp(args.random, args.seed, args.stock,args.viajes,args.precios)
    x = g.GRASP_Solution(float(args.a_val),int(args.lcr),1,test=args.test)
    sol[i] = x[0]
    val[i] = x[1]
    trans[i] = x[2]


with open("Resumen_test.csv", 'a') as csvfile:
    writer = csv.writer(csvfile,delimiter=';')    
    new_val = 0
    new_sol = {}
    new_trans = {}
    for i in val:
        if args.debug:
            print("---> Iter {} alfa {} fitness: {:.2f} transporte: {:.2f}".format(i,args.a_val,val[i],trans[i]))
        if args.test:
            writer.writerow([i,args.lcr,args.a_val,val[i],trans[i]])
        if new_val == 0:
            new_val = val[i]
            new_sol = sol[i]
            new_trans =  trans[i]
        elif val[i] < new_val:
            new_val = val[i]
            new_sol = sol[i]
            new_trans =  trans[i]
    val = new_val
    sol = new_sol
    trans = new_trans

if(args.save and not args.test):
    with open(args.name+str(args.iteraciones)+"_"+str(args.lcr)+"_"+str(old_aval)+'.json', 'w') as outfile:
        json.dump(sol, outfile)

if args.debug:
    print("---> Mejor fitness: {:.2f} Transporte: {:.2f}".format(val,trans))   
    print("--- {} seconds ---".format(time.time() - start_time))
