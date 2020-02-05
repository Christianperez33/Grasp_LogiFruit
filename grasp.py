import datetime
import os
from getData import DatosStock
from getData import DatosViajes
from getData import DatosPrecio
from collections import OrderedDict
from operator import itemgetter 
import numpy as np
import collections
import operator
import time
import random
import csv
import copy


class Grasp:
    """
     Clase Grasp contiene los metodos necesarios para la correcta obtención de los datos y su procesado para obtener una solución válida
    """

    def __init__(self, shuffle=True, seed=None, stock="./data/stock.csv", viajes ="./data/viajes.csv", precios = "./data/precio.csv"):
        """
        __init__ Constructor que inicializa las variables de stock y viajes segun las funciones desarrolladas para la obtención de los datos
        """
        self.solucion = dict()
        self.stock = DatosStock(stock)
        self.oriStock = copy.deepcopy(self.stock.dictStock)
        self.viajes = DatosViajes(viajes)
        self.oriViajes = copy.deepcopy(self.viajes.dictViajes)
        self.precios = DatosPrecio(precios)
        self.oriPrecios = copy.deepcopy(self.precios.dictPrecios)


        if shuffle:
            keys_stock = list(self.oriStock.keys())
            keys_viajes = list(self.oriViajes.keys())
            
            if seed is None:
                random.seed()
            else:
                random.seed(seed)
                
            random.shuffle(keys_stock)
            random.shuffle(keys_viajes)

            shuffled_stock = dict()
            for key in keys_stock:
                shuffled_stock.update({key: self.oriStock[key]})
                
            shuffled_viajes = dict()
            for key in keys_viajes:
                shuffled_viajes.update({key: self.oriViajes[key]})

            self.oriStock  = shuffled_stock
            self.oriViajes = shuffled_viajes
        #! dict --> {'idViaje':{ 'idPlataforma':{'Precio': str(float), 'Demora':str}, ...}, ...}
        self.datos = self.getData()
        
    def getData(self):
        """
        getData Función que preprocesa los datos para su posterior uso

        Returns:
            dict --> {'idViaje':{ 'idPlataforma':{'Precio': str(float), 'Demora':str}, ...}, ...}
        """
        self.dictStock   = copy.deepcopy(self.oriStock)
        self.dictViajes  = copy.deepcopy(self.oriViajes)
        self.dictPrecios = copy.deepcopy(self.oriPrecios)


        output = dict(zip(set(self.dictViajes), [
                      {} for v in set(self.dictViajes)]))
        for viaje in self.dictViajes:

            fecha = self.dictViajes[viaje]['FechaDescarga']
            if self.dictViajes[viaje]['PlataformasPosibles'] is None: continue
            
            plataformas = self.dictViajes[viaje]['PlataformasPosibles']['CosteTransporte']
            plataformas = plataformas if isinstance(
                plataformas, list) else [plataformas]

            articulos = self.dictViajes[viaje]['Carga']['CantidadModelo']
            articulos = articulos if isinstance(
                articulos, list) else [articulos]

            for plataforma in plataformas:
                idPlataforma = plataforma['Plataforma']
                
                coste = float(plataforma['Precio'])
                demora = plataforma['Demora']
                if len(plataformas) == 1:
                    for articulo in articulos:
                        idArticulo = articulo['Articulo']
                        cantidad = int(articulo['Cantidad'])
                        fechas = list(self.dictStock[idPlataforma][idArticulo].keys())
                        
                        ini_rango = (fechas.index(fecha)) - int(demora)
                        rango = fechas[0 if ini_rango <= 0 else ini_rango:]
                        for f in rango:
                            self.dictStock[idPlataforma][idArticulo][f] = int(self.dictStock[idPlataforma][idArticulo][f]) - cantidad
                        
                        # if int(idArticulo) == 81 and int(idPlataforma) == 7 :
                        #     print(cantidad)
                        #     print(fecha)
                        #     print(demora)
                        #     print(self.oriStock['7']["81"].values())
                        #     print(self.dictStock['7']["81"].values())
                        #     os._exit(0)

                    self.solucion[viaje] = plataforma['Plataforma']
                    del output[viaje]
                else:
                    output[viaje][plataforma['Plataforma']] = plataforma
        
        return output

    def GRASP_Solution(self, alfa=0.5,LCR=3, iter=0):
        
        listaLCR = {s: len(self.datos[s]) for s in self.datos}
        listaLCR = sorted(listaLCR.items(),
                          key=operator.itemgetter(1),
                          reverse=False)
        # viajes con cada una de las plataformas
        actual = listaLCR[:LCR-1]
        resto = listaLCR[LCR-1:]
        total_fitness = 0
        coste_transporte = 0
        while len(actual) > 0 :

            if len(resto) > 0:
                val = resto.pop(0)
                actual.append(val)
                fecha = self.dictViajes[val[0]]['FechaDescarga']

            fitness_viajes = {}
            fitness_valores = {}
            for id_viaje, nplat in actual:
                articulos = [self.dictViajes[id_viaje]['Carga']['CantidadModelo']] if type(self.dictViajes[id_viaje]['Carga']['CantidadModelo']) != list else self.dictViajes[id_viaje]['Carga']['CantidadModelo']
                stocks = {}
                cantidades ={}
                restos = {}
                for articulo in articulos:
                    # obtenemos los datos del articulo
                    idArticulo = articulo['Articulo']
                    cantidad = abs(int(articulo['Cantidad']))
                    precio = self.oriPrecios[idArticulo]["PrecioUnitario"]
                    stocks[idArticulo] = {}
                    cantidades[idArticulo] = {}
                    restos[idArticulo] = {}
                    # recorremos todas las plataformas por cada articulo para obtener su stock
                    for id_plataforma in self.datos[id_viaje]:
                        demora = self.datos[id_viaje][id_plataforma]['Demora']
                        fechas = list(self.dictStock[id_plataforma][idArticulo].keys())
                        costeStock = 0
                        cantidadStock = 0
                        resto_stock = 0
                        # verificamos si es una fecha válida
                        if fecha in fechas:
                            if fechas.index(fecha)-int(demora) > 0:
                                # ? se restan las catidades de ese articulo a cada uno de los dias en los que se usa
                                for d in range(int(demora)):
                                    resto_stock = resto_stock + int(self.dictStock[id_plataforma][idArticulo][fechas[fechas.index(fecha) - d]]) - cantidad
                                    cantidadStock = cantidadStock + int(self.dictStock[id_plataforma][idArticulo][fechas[fechas.index(fecha) - d]])
                                    if resto_stock < 0:
                                        costeStock = costeStock + int(self.dictStock[id_plataforma][idArticulo][fechas[fechas.index(fecha) - d]]) - cantidad * precio
                                cantidadStock = (cantidadStock/int(demora)) if cantidadStock > 0 else 0
                                resto_stock = (resto_stock/int(demora)) if resto_stock > 0 else 0
                            else:
                                resto_stock = resto_stock + int(self.dictStock[id_plataforma][idArticulo][fecha]) - cantidad
                                cantidadStock = cantidadStock + int(self.dictStock[id_plataforma][idArticulo][fecha])
                                if resto_stock < 0:
                                    costeStock = costeStock + int(self.dictStock[id_plataforma][idArticulo][fecha]) - cantidad * precio

                        stocks[idArticulo][id_plataforma] = costeStock
                        cantidades[idArticulo][id_plataforma] = cantidadStock
                        restos[idArticulo][id_plataforma] = resto_stock
                
                # aplanamos el dict para que todos los valores de los articulos en todas las plataformas generen el coste
                counter = collections.Counter()
                for d in stocks.values():
                    counter.update(d)
                stocks = dict(counter)

                counter = collections.Counter()
                for d in cantidades.values():
                    counter.update(d)
                cantidades = dict(counter)

                counter = collections.Counter()
                for d in restos.values():
                    counter.update(d)
                restos = dict(counter)

                fitness_plats_precio = {}
                fitness_plats_cantidad = {}
                fitness_transporte = {}
                fitness_completo_precio = {}
                fitness_completo_cantidad = {}
                for id_plataforma in self.datos[id_viaje]:

                    #  Calculos para el coste de transporte 
                    fitness_transporte[id_plataforma] = float(self.datos[id_viaje][id_plataforma]['Precio'])
                    
                    #  Calculos para el coste del stock
                    # Función fitness
                    fitness_plats_precio[id_plataforma] = stocks[id_plataforma]
                    fitness_completo_precio[id_plataforma] = alfa * fitness_transporte[id_plataforma] + (1 - alfa) * fitness_plats_precio[id_plataforma]
                    
                    #  Calculos para la cantidad de stock
                    # Función fitness en el caso de que todas las plataformas tengan stock positivo
                    fitness_plats_cantidad[id_plataforma] = restos[id_plataforma]
                    fitness_completo_cantidad[id_plataforma] = alfa * fitness_transporte[id_plataforma] + (1 - alfa) * fitness_plats_cantidad[id_plataforma]


                #Obtención del mejor fitness por stock/precio
                id_plataforma_select = min(fitness_completo_precio.items(), key=operator.itemgetter(1))[0]
                if fitness_plats_precio[id_plataforma_select] != 0:
                    zero_dict = {x:y for x,y in fitness_plats_precio.items() if y == 0 }
                    if len(zero_dict) == 0:
                        id_plataforma_select = min(fitness_plats_precio.items(), key=operator.itemgetter(1))[0]
                        fitness_valores[id_viaje] = fitness_completo_precio[id_plataforma_select]
                        fitness_viajes[id_viaje] = id_plataforma_select
                    else:
                        cantidad_dict = {x:fitness_plats_cantidad[x] for x in zero_dict.keys()}
                        id_plataforma_select = min(fitness_plats_cantidad.items(), key=operator.itemgetter(1))[0]
                        fitness_valores[id_viaje] = fitness_completo_precio[id_plataforma_select]
                        fitness_viajes[id_viaje] = id_plataforma_select
                else:
                    fitness_valores[id_viaje] = fitness_completo_precio[id_plataforma_select]
                    fitness_viajes[id_viaje] = id_plataforma_select


            # evaluacion de los fitness del lcr
            id_viaje_select = min(fitness_valores.items(), key=operator.itemgetter(1))[0]
            plataforma_viaje_select = fitness_viajes[id_viaje_select]
            total_fitness = total_fitness + fitness_valores[id_viaje_select]
            coste_transporte = coste_transporte + fitness_transporte[fitness_viajes[id_viaje_select]]
            
            # eliminamos de la lista el viaje que ya hemos adjudicado
            list_actual = dict(actual)
            del list_actual[id_viaje_select]
            actual = list(list_actual.items()) 
            # añadimos a la solcuión el viaje calculado
            self.solucion[id_viaje_select] = plataforma_viaje_select

            
            #actualizamos el stock para poder ver el balanceo
            fechas = []
            
            # obtenemos la demora de las plataformas 
            plataformas = self.oriViajes[id_viaje_select]['PlataformasPosibles']['CosteTransporte']
            plataformas = plataformas if isinstance(plataformas, list) else [plataformas]
            for plataforma in plataformas:
                if str(plataforma['Plataforma']) == str(plataforma_viaje_select):
                    demora = plataforma['Demora']
                    break
                       
            articulos = self.oriViajes[id_viaje_select]['Carga']['CantidadModelo']
            articulos = articulos if isinstance(articulos, list) else [articulos]
            for articulo in articulos:
                idArticulo = articulo['Articulo']
                cantidad = abs(int(articulo['Cantidad']))
                fecha = self.dictViajes[id_viaje_select]['FechaDescarga']
                fechas = list(self.dictStock[plataforma_viaje_select][idArticulo].keys())
                
                ini_rango = (fechas.index(fecha)) - int(demora)
                rango = fechas[0 if ini_rango <= 0 else ini_rango:]
                for f in rango:
                    self.dictStock[plataforma_viaje_select][idArticulo][f] = int(self.dictStock[plataforma_viaje_select][idArticulo][f]) - cantidad


                
        # guardamos el diccionario de stock para poder ver el balanceo
        dictstock = dict(OrderedDict(sorted(self.dictStock.items(), key = lambda t: int(t[0]))))
        with open("stock_sol_"+str(iter+1)+"_"+str(LCR)+"_"+str(int(alfa*100))+".csv", 'w') as csvfile:
            writer = csv.writer(csvfile,delimiter=';')
            for p in dictstock:
                writer.writerow([int(p),' ',' ',' ',' ',' ',' ',' ',' '])
                writer.writerow([' ']+fechas)
                for a in dictstock[p]:
                    writer.writerow([int(a)]+list(dictstock[p][a].values()))
                writer.writerow([' '])
                
            
        return [self.solucion, total_fitness/len(listaLCR),coste_transporte/len(listaLCR)]