import time
from grasp import *
import argparse
from tqdm import tqdm
import json
from multiprocessing import cpu_count
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
argparser.add_argument('-m', '--mode', help='Mode de prueba(n_plat,n_plat+sumart...', default=2)
argparser.add_argument('-b', '--beta', help='Mode de balanceo noramlizacion', default=50)
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
alfas = {}
sum_val = {}
sol_zonas = {}
art_min = {}
suma_minimo = {}
cuantos_minimo = {}
media_minimo = {}

if args.debug:
    print("Config: Inter -> {},\n \tAlfa -> {},\n \tLCR ->{},\n \tAutosave -> {}".format(args.iteraciones,args.a_val ,args.lcr,args.save))
    

for i in tqdm(range(int(args.iteraciones)),disable=(not args.debug)):
    g = Grasp(args.random, args.seed, args.stock,args.viajes,args.precios)
    x = g.GRASP_Solution(int(args.beta),int(args.mode),float(args.a_val),int(args.lcr),1,test=args.test)
    sol[i] = x[0]
    val[i] = x[1]
    trans[i] = x[2]
    alfas[i] = x[3]
    sol_zonas[i] = x[4]
    art_min[i] = x[5]
    suma_minimo[i] = x[6]
    cuantos_minimo[i] = x[7]
    media_minimo[i] = x[8]
    


with open("Resumen_test.csv", 'a',newline='') as csvfile:
    writer = csv.writer(csvfile,delimiter=';')
    writer.writerow([' ',' ','alfa final','Coste stock','Coste transporte','Stock minimo','Total minimos','Numero articulos en minimos','Media'])    
    new_val = 0
    new_sol = {}
    new_trans = {}
    new_sol_zonas = {}
    for i in val:

        print("---> Iter {} alfa_ini {} alfa_fin {:.5f} fitness: {:.2f} transporte: {:.2f}".format(i,args.a_val,alfas[i],val[i],trans[i]))
        if args.test:
            writer.writerow([i,args.a_val,round(alfas[i],2),round(val[i],2),round(trans[i],2),art_min[i],suma_minimo[i],cuantos_minimo[i],round(media_minimo[i],2)])
        if new_val == 0:
            new_val = val[i]
            new_sol = sol[i]
            new_trans =  trans[i]
            new_sol_zonas = sol_zonas[i] 
        elif val[i] < new_val:
            new_val = val[i]
            new_sol = sol[i]
            new_trans =  trans[i]
            new_sol_zonas = sol_zonas[i] 
    val = new_val
    sol = new_sol
    trans = new_trans
    sol_zonas = new_sol_zonas

if(args.save):
    print(type(sol))
    with open(args.name+str(args.iteraciones)+"_"+str(args.lcr)+"_"+str(old_aval)+'.json', 'w') as outfile:
        sol.update({'CT':trans})
        json.dump(sol, outfile)
    with open(args.name+str(args.iteraciones)+"_"+str(args.lcr)+"3333"+str(old_aval)+'.json', 'w') as outfile:
       json.dump(trans, outfile)
    # with open(args.name+str(args.iteraciones)+"_"+str(args.lcr)+"_"+str(old_aval)+'_ZONAS.json', 'w') as outfile:
    #    json.dump(sol_zonas, outfile)
        

if args.debug:
    print("---> Mejor fitness: {:.2f} Transporte: {:.2f}".format(val,trans))   
    print("--- {} seconds ---".format(time.time() - start_time))
