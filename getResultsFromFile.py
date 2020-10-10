import time
from grasp import *
import argparse
from tqdm import tqdm
import json
from Genetic.getData import DatosStock
from Genetic.getData import DatosViajes
from Genetic.getData import DatosPrecio
import os
import copy
argparser = argparse.ArgumentParser()
argparser.add_argument('-x', '--stock')
argparser.add_argument('-y', '--viajes')
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
        articulos = [dictViajes[id_viaje]['Carga']['CantidadModelo']] if type(dictViajes[id_viaje]['Carga']['CantidadModelo']) != list else dictViajes[id_viaje]['Carga']['CantidadModelo']

        stocks = {}
        cantidades ={}
        restos = {}
        fecha = dictViajes[id_viaje]['FechaDescarga']
        ## Es necesario obtener la demora de la plataforma para el viaje estudiado
        plataformas = oriViajes[id_viaje]['PlataformasPosibles']['CosteTransporte']
        plataformas = plataformas if isinstance(plataformas, list) else [plataformas]
       
        demora = [p["Demora"] for p in plataformas if str(p['Plataforma']) == str(id_plat)]
        demora = demora[0]

        ## Recorremos los articulos de cada viaje   
        for articulo in articulos:
            idArticulo = articulo['Articulo']
            cantidad = abs(int(articulo['Cantidad']))
            precio = oriPrecios[idArticulo]["PrecioUnitario"]
            stocks[idArticulo] = {}
            cantidades[idArticulo] = {}
            restos[idArticulo] = {}
            ## Obtenemos las fechas del diccionario de stock para cruzar con las fechas del viaje y su demora
            fechas = list(dictStock[id_plat][idArticulo].keys())
            coste_stock_aux = 0
            resto_stock = 0
            # verificamos si es una fecha válida
            if fecha in fechas:
                if fechas.index(fecha)-int(demora) > 0:
                    # ? se restan las catidades de ese articulo a cada uno de los dias en los que se usa
                    for d in range(fechas.index(fecha)-int(demora),len(fechas)+1):
                        resto_unitario =  int(dictStock[id_plat][idArticulo][fechas[fechas.index(fecha) - d]]) - cantidad
                        if resto_unitario < 0:
                            coste_stock_aux = coste_stock_aux + ( resto_unitario * precio)
                        resto_stock = resto_stock + resto_unitario
                    resto_stock = (resto_stock/len(range(fechas.index(fecha)-int(demora),len(fechas)+1))) if resto_stock > 0 else 0
                else:
                    # ? se restan las catidades de ese articulo a cada uno de los dias en los que se usa
                    for d in range(fechas.index(fecha),len(fechas)+1):
                        resto_unitario =  int(dictStock[id_plat][idArticulo][fechas[fechas.index(fecha) - d]]) - cantidad
                        if resto_unitario < 0:
                            coste_stock_aux = coste_stock_aux + (resto_unitario * precio)
                        resto_stock = resto_stock + resto_unitario
                    resto_stock = (resto_stock/len(range(fechas.index(fecha),len(fechas)+1))) if resto_stock > 0 else 0
            #coste_stock_articulo=coste_stock_articulo+coste_stock_aux
            stocks[idArticulo] = coste_stock_aux

            fechas = list(dictStock[id_plat][idArticulo].keys())
                
            ini_rango = (fechas.index(fecha)) - int(demora)
            rango = fechas[0 if ini_rango <= 0 else ini_rango:]
            for f in rango:
                dictStock[id_plat][idArticulo][f] = int(dictStock[id_plat][idArticulo][f]) - cantidad
        coste_stock=coste_stock+abs(sum(stocks.values()))
     # Función fitness
    fitness_completo_precio= ((alfa/100) * coste_transporte) + ((1 - (alfa/100)) * (coste_stock))
    return ((fitness_completo_precio/n_travel),(coste_transporte/n_travel),(coste_stock/n_travel))

ss = ""

for filename in os.listdir(args.dir):
    dictStock  = copy.deepcopy(oriStock)
    file = open(args.dir+filename, "rb")
    sol = json.loads(file.read())
    fit,ct,cs= calculate_fitness(sol,90,len(sol))
    ss += str((ct,cs,ct+cs/1906))+", "

print("["+ss+"]")
