import time
from genetic import *
import argparse
from tqdm import tqdm
import os

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
argparser.add_argument('-i', '--iter', help='numero de iteraciones del AG', default=1)
argparser.add_argument('-m', '--mutate', help='probabilidad de mutacion', default=2)
argparser.add_argument('-c', '--crossover', help='parametro de cruzamiento', default=50)
argparser.add_argument('-a', '--alfa', help='parametro alfa del fitness', default=90)
argparser.add_argument('-ag', '--max_age', help='proporción de edad maxíma en referncia a las iteraciones', default=10)
argparser.add_argument('-ns', '--n_son', help='numero de hijos en la funcion de reproduccion', default=2)
argparser.add_argument('-ng', '--n_sup', help='numero de representantes de una familia que avanza de generacion', default=2)
args = argparser.parse_args()
start_time = time.time()

if int(args.n_son)+2>=int(args.n_sup):
    g = Genetic(int(args.alfa))
    [x,y] = develope(g,int(args.iter),int(args.mutate),int(args.crossover),int(args.alfa),int(args.max_age),int(args.n_son),int(args.n_sup))
    best=get_best_solution(x)
    create_excel(g,best,y,"final")
    print("--- {} seconds ---".format(time.time() - start_time))
else:
    print("ERROR PARAMETROS DE ENTRADA: El numero de miembros de la nueva generacion no peude ser mayor que el numero de hijos")
    os._exit(0)
