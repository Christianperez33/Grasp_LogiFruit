import datetime
import os
from getData import DatosStock
from getData import DatosViajes
from getData import DatosPrecio
from collections import OrderedDict
import numpy as np
import collections
import operator
import time
import random
import csv


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
        self.oriStock = self.stock.dictStock
        self.viajes = DatosViajes(viajes)
        self.oriViajes = self.viajes.dictViajes
        self.precios = DatosPrecio(precios)
        self.oriPrecios = self.precios.dictPrecios


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
        self.ini_sol = self.getData()
        
    def getData(self):
        """
        getData Función que preprocesa los datos para su posterior uso

        Returns:
            dict --> {'idViaje':{ 'idPlataforma':{'Precio': str(float), 'Demora':str}, ...}, ...}
        """
        self.dictStock   = self.oriStock
        self.dictViajes  = self.oriViajes
        self.dictPrecios = self.oriPrecios


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
                        fechas = list(
                            self.dictStock[idPlataforma][idArticulo].keys())
                        if fecha in fechas:
                            if fechas.index(fecha)-int(demora) > 0:
                                cantidadStock = 0
                                # ? se restan las catidades de ese articulo a cada uno de los diás en los que se usa
                                for d in range(int(demora)):
                                    cantidadStock = cantidadStock + \
                                        int(self.dictStock[idPlataforma][idArticulo][fechas[fechas.index(
                                            fecha) - d]]) - cantidad
                                    self.dictStock[idPlataforma][idArticulo][fechas[fechas.index(
                                        fecha) - d]] = str(cantidadStock)
                            else:
                                cantidadStock = int(
                                    self.dictStock[idPlataforma][idArticulo][fecha]) - cantidad
                                self.dictStock[idPlataforma][idArticulo][fecha] = str(
                                    cantidadStock)

                    self.solucion[viaje] = plataforma['Plataforma']
                    del output[viaje]
                else:
                    output[viaje][plataforma['Plataforma']] = plataforma
                    # del output[viaje][plataforma['Plataforma']]['Plataforma']

        return output

    def GRASP_Solution(self, alfa=0.5,LCR=3, iter=0):
        listaLCR = {s: len(self.ini_sol[s]) for s in self.ini_sol}
        listaLCR = sorted(listaLCR.items(),
                          key=operator.itemgetter(1),
                          reverse=False)
        # viajes con cada una de las plataformas
        init = listaLCR[:LCR-1]
        resto = listaLCR[LCR-1:]
        total_fitness = 0
        while len(init) > 0 :
            if len(resto) > 0:
                val = resto.pop(0)
                init.append(val)
                fecha = self.dictViajes[val[0]]['FechaDescarga']
            fitness_viajes = {}
            fitness_valores = {}
            
            for id_viaje, nplat in init:
                articulos = [self.dictViajes[id_viaje]['Carga']['CantidadModelo']] if type(self.dictViajes[id_viaje]['Carga']['CantidadModelo']) != list else self.dictViajes[id_viaje]['Carga']['CantidadModelo']
                stocks = {}
                for articulo in articulos:
                    # obtenemos los datos del articulo
                    idArticulo = articulo['Articulo']
                    cantidad = int(articulo['Cantidad'])
                    precio = self.oriPrecios[idArticulo]["PrecioUnitario"]
                    stocks[idArticulo] = {}
                    # recorremos todas las plataformas por cada articulo para obtener su stock
                    for id_plataforma in self.ini_sol[id_viaje]:
                        demora = self.ini_sol[id_viaje][id_plataforma]['Demora']
                        fechas = list(self.dictStock[id_plataforma][idArticulo].keys())
                        costeStock = 0
                        # verificamos si es una fecha válida
                        if fecha in fechas:
                            if fechas.index(fecha)-int(demora) > 0:
                                # ? se restan las catidades de ese articulo a cada uno de los dias en los que se usa
                                for d in range(int(demora)):
                                    costeStock = int(self.dictStock[id_plataforma][idArticulo][fechas[fechas.index(fecha) - d]]) - cantidad
                            else:
                                costeStock = int(self.dictStock[id_plataforma][idArticulo][fecha]) - cantidad
                        if costeStock >= 0:
                            costeStock = 0
                        else:
                            costeStock = abs(costeStock * precio)
                        stocks[idArticulo][id_plataforma] = costeStock
                

                # aplanamos el dict para que todos los valores de los articulos en todas las plataformas generen el coste
                counter = collections.Counter()
                for d in stocks.values():
                    counter.update(d)
                stocks = dict(counter)

                fitness_plats = {}
                for id_plataforma in self.ini_sol[id_viaje]:

                    #  Calculos para el coste de transporte 
                    ct = float(self.ini_sol[id_viaje][id_plataforma]['Precio'])
                    
                    #  Calculos para el coste del stock
                    cs = stocks[id_plataforma]
                    # Función fitness
                    fitness_plats[id_plataforma] = alfa*ct + (1-alfa)*cs
                # obtenemos la plataforma con mayor fitness y su valor
                fitness_viajes[id_viaje] = min(fitness_plats.items(), key=operator.itemgetter(1))[0] 
                fitness_valores[id_viaje] = fitness_plats[min(fitness_plats.items(), key=operator.itemgetter(1))[0]]
            
            # evaluacion de los fitnees del lcr
            id_viaje_select = max(fitness_valores.items(), key=operator.itemgetter(1))[0]
            plataforma_viaje_select = fitness_viajes[id_viaje_select]
            total_fitness = total_fitness + fitness_valores[id_viaje_select]
            
            # eliminamos de la lista el viaje que ya hemos adjudicado
            list_init = dict(init)
            del list_init[id_viaje_select]
            init = list(list_init.items()) 
            # añadimos a la solcuión el viaje calculado
            self.solucion[id_viaje_select] = plataforma_viaje_select


        #actualizamos el stock para poder ver el balanceo
        for idviaje in self.solucion:
            idplataforma = self.solucion[idviaje]
            
            plataformas = self.oriViajes[idviaje]['PlataformasPosibles']['CosteTransporte']
            plataformas = plataformas if isinstance(plataformas, list) else [plataformas]
            for plataforma in plataformas:
                if str(plataforma['Plataforma']) == str(idplataforma):
                    demora = plataforma['Demora']
                    break
                    
            articulos = self.oriViajes[idviaje]['Carga']['CantidadModelo']
            articulos = articulos if isinstance(articulos, list) else [articulos]
            for articulo in articulos:
                idArticulo = articulo['Articulo']
                cantidad = int(articulo['Cantidad'])
                fechas = list(self.dictStock[idplataforma][idArticulo].keys())
                if fecha in fechas:
                    if fechas.index(fecha)-int(demora) > 0:
                        for d in range(int(demora)):
                            self.dictStock[id_plataforma][idArticulo][fechas[fechas.index(fecha) - d]] = int(self.dictStock[id_plataforma][idArticulo][fechas[fechas.index(fecha) - d]]) - cantidad
                    else:
                        self.dictStock[id_plataforma][idArticulo][fecha] = int(self.dictStock[id_plataforma][idArticulo][fecha]) - cantidad
        
        
        # guardamos el diccionario de stock para poder ver el balanceo
        dictstock = dict(OrderedDict(sorted(self.dictStock.items(), key = lambda t: int(t[0]))))
        with open("stock_sol_"+str(iter)+".csv", 'w') as csvfile:
            writer = csv.writer(csvfile,delimiter=';')
            for p in dictstock:
                writer.writerow([int(p),' ',' ',' ',' ',' ',' ',' ',' '])
                for a in dictstock[p]:
                    writer.writerow([int(a)]+list(dictstock[p][a].values()))
                writer.writerow([' '])
                
            
        return [self.solucion, total_fitness/len(listaLCR)]