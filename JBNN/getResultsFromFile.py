import time
from GRASP.grasp import *
import argparse
from tqdm import tqdm
import json
from Genetic.getData import DatosStock
from Genetic.getData import DatosViajes
from Genetic.getData import DatosPrecio
import os
import copy
argparser = argparse.ArgumentParser()
argparser.add_argument('-x', '--stock', default="./Genetic/data_grasp/stock.csv")
argparser.add_argument('-y', '--viajes', default="./Genetic/data_grasp/viajes.xml")
argparser.add_argument('-z', '--precios', default="./Genetic/data_grasp/precios.csv")
argparser.add_argument('-d', '--dir')
args = argparser.parse_args()

# stockORI = DatosStock(args.stock)
# preciosORI = DatosPrecio(args.precios)
# viajesORI = DatosViajes(args.viajes)
alfa=90
viajes = DatosViajes(args.viajes)
oriViajes = copy.deepcopy(viajes.dictViajes)
dictViajes  = copy.deepcopy(oriViajes)
stock = DatosStock(args.stock)  
oriStock = copy.deepcopy(stock.dictStock)
dictStock   = copy.deepcopy(oriStock)
precios = DatosPrecio(args.precios)
oriPrecios = copy.deepcopy(precios.dictPrecios)

def calculate_fitness(member,alfa,n_travel): # Esta función calcula la formula del fitness para una solucion, dado un alfa con el que realizar el calculo con coste de transporte(CT) y coste de stock (CS)
    ## FORMULA FITNESS: (ALFA * CT)  + ((1-ALFA) * CS)
    ## CT-> Coste de transporte, para cda viaje sumar el coste de transporte de su plataforma asignada
    dictStock  = copy.deepcopy(oriStock)
    coste_transporte = 0
    for s in member:
        cosas = oriViajes[s]['PlataformasPosibles']['CosteTransporte']
        cosas = cosas if isinstance(cosas, list) else [cosas]
        for c in cosas:
            if int(c['Plataforma']) == int(member[s]):
                coste_transporte = coste_transporte + float(c['Precio'])
    ## CS-> Coste de stock, recorremos todos los viajes plataforma de la solucion, comprobando si el stock de las plataformas es negativo y sumando el coste de reponer ese stock
    coste_stock=0

    for id_viaje,id_plat in member.items():
        articulos = [dictViajes[id_viaje]['Carga']['CantidadModelo']] if not isinstance(dictViajes[id_viaje]['Carga']['CantidadModelo'], list) else dictViajes[id_viaje]['Carga']['CantidadModelo']

        stocks = {}
        cantidades = {}
        fecha = dictViajes[id_viaje]['FechaDescarga']
        ## Es necesario obtener la demora de la plataforma para el viaje estudiado
        plataformas = oriViajes[id_viaje]['PlataformasPosibles']['CosteTransporte']
        plataformas = plataformas if isinstance(plataformas, list) else [plataformas]
       
        demora = [p["Demora"] for p in plataformas if str(p['Plataforma']) == str(id_plat)][0]

        ## Recorremos los articulos de cada viaje   
        for articulo in articulos:
            idArticulo = articulo['Articulo']
            cantidad = abs(int(articulo['Cantidad']))
            precio = oriPrecios[idArticulo]["PrecioUnitario"]
            cantidades[idArticulo] = {}
            ## Obtenemos las fechas del diccionario de stock para cruzar con las fechas del viaje y su demora
            fechas = list(dictStock[id_plat][idArticulo].keys())
            coste_stock_aux = 0

            init =fechas.index(fecha)-int(demora) if fechas.index(fecha)-int(demora) > 0 else fechas.index(fecha)

            # ? se restan las catidades de ese articulo a cada uno de los dias en los que se usa
            for d in range(init,len(fechas)+1):
                resto_unitario =  int(dictStock[id_plat][idArticulo][fechas[fechas.index(fecha) - d]]) - cantidad
                coste_stock_aux += (abs(resto_unitario) * precio if resto_unitario < 0 else 0)
                dictStock[id_plat][idArticulo][fechas[fechas.index(fecha) - d]] = resto_unitario

            stocks[idArticulo] = coste_stock_aux

        coste_stock +=  abs(sum(stocks.values()))
    # Función fitness
    fitness_completo_precio= ((alfa/100) * coste_transporte) + ((1 - (alfa/100)) * (coste_stock))
    # fitness_completo_precio=  coste_transporte + coste_stock/n_travel
    return ((fitness_completo_precio),(coste_transporte/n_travel),coste_stock)

ss = ""

for filename in os.listdir(args.dir):
    dictStock  = copy.deepcopy(oriStock)
    file = open(args.dir+filename, "rb")
    sol = json.loads(file.read())
    fit,ct,cs= calculate_fitness(sol,90,len(sol))
    ss += str((ct,cs/len(sol),ct+cs/len(sol)))+", "
    print((filename,ct,cs/len(sol),ct+cs/len(sol)))
# print("["+ss+"]")