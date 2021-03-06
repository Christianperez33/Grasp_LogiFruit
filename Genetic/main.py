
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
argparser.add_argument('-m', '--mutate', help='probabilidad de mutacion', default=0.5)
argparser.add_argument('-c', '--crossover', help='parametro de cruzamiento', default=50)
argparser.add_argument('-a', '--alfa', help='parametro alfa del fitness', default=90)
argparser.add_argument('-ag', '--max_age', help='proporción de edad maxíma en referncia a las iteraciones', default=100)
argparser.add_argument('-ns', '--n_son', help='numero de hijos en la funcion de reproduccion', default=2)
argparser.add_argument('-ng', '--n_sup', help='numero de representantes de una familia que avanza de generacion', default=2)
argparser.add_argument('-x', '--stock', help='Path al fichero csv de stock', default="./data/stock.csv")
argparser.add_argument('-y', '--viajes', help='Path al fichero xml de viajes', default="./data/viajes.xml")
argparser.add_argument('-z', '--precios', help='Path al fichero csv de precios', default="./Genetic/data_grasp/precios.csv")
argparser.add_argument('-s', '--solpath')
args = argparser.parse_args()
start_time = time.time()

if int(args.n_son)+2>=int(args.n_sup):
    g = Genetic(int(args.alfa),args.viajes,args.stock,args.precios,args.solpath)
    [x,y] = develope(g,int(args.iter),float(args.mutate),int(args.crossover),int(args.alfa),int(args.max_age),int(args.n_son),int(args.n_sup))
    best,bfitness=min(x.items(),key=lambda x:x[1])
    print(best)
    print(bfitness)
    with open('./Genetic/results/json/solution'+str(args.solpath.split("/")[-3])+'_'+args.iter+'.json', 'w') as outfile:
        json.dump(y[best], outfile)
    # create_excel(g,best,y,"final")
    
    print("--- {} seconds ---".format(time.time() - start_time))
else:
    print("ERROR PARAMETROS DE ENTRADA: El numero de miembros de la nueva generacion no peude ser mayor que el numero de hijos")
    os._exit(0)
