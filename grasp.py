import datetime
import os
from getData import DatosStock
from getData import DatosViajes
from collections import OrderedDict
import numpy as np
import collections
import operator
import time

class Grasp:
    """
     Clase Grasp contiene los metodos necesarios para la correcta obtención de los datos y su procesado para obtener una solución válida
    """

    def __init__(self):
        """
        __init__ Constructor que inicializa las variables de stock y viajes segun las funciones desarrolladas para la obtención de los datos
        """
        self.solucion = dict()
        self.stock = DatosStock("data/stock.csv")
        self.oriStock = self.stock.dictStock
        self.viajes = DatosViajes("data/viajes.xml")
        self.oriViajes = self.viajes.dictViajes
        # ? dict --> {'idViaje':{ 'idPlataforma':{'Precio': str(float), 'Demora':str}, ...}, ...}
        self.ini_sol = self.getData()

    def getData(self):
        """
        getData Función que preprocesa los datos para su posterior uso

        Returns:
            dict --> {'idViaje':{ 'idPlataforma':{'Precio': str(float), 'Demora':str}, ...}, ...}
        """
        self.dictStock = self.oriStock
        self.dictViajes = self.oriViajes
        output = dict(zip(set(self.dictViajes), [
                      {} for v in set(self.dictViajes)]))
        for viaje in self.dictViajes:

            fecha = self.dictViajes[viaje]['FechaDescarga']

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
                    del output[viaje][plataforma['Plataforma']]['Plataforma']

        return output

    def GRASP_Solution(self, LCR=3):
        listaLCR = {s: len(self.ini_sol[s]) for s in self.ini_sol}
        listaLCR = sorted(listaLCR.items(),
                          key=operator.itemgetter(1),
                          reverse=False)

        # viajes con cada una de las plataformas
        init = listaLCR[:LCR-1]
        resto = listaLCR[LCR-1:]
        for val in resto:
            init.append(val)
            fecha = self.dictViajes[val[0]]['FechaDescarga']
            fitness_viajes = {}
            fitness_valores = {}
            for id_viaje, nplat in init:
                articulos = [self.dictViajes[id_viaje]['Carga']['CantidadModelo']] if type(self.dictViajes[id_viaje]['Carga']['CantidadModelo']) != list else self.dictViajes[id_viaje]['Carga']['CantidadModelo']
                
                stocks = {}
                #  Calculos para el coste de stock normalizado
                for articulo in articulos:
                    idArticulo = articulo['Articulo']
                    cantidad = int(articulo['Cantidad'])
                    stock_plat = {idArticulo:{}}
                    suma_art_plat = 0
                    for id_plataforma in self.ini_sol[id_viaje]:
                        demora = self.ini_sol[id_viaje][id_plataforma]['Demora']
                        fechas = list(self.dictStock[id_plataforma][idArticulo].keys())
                        if fecha in fechas:
                            if fechas.index(fecha)-int(demora) > 0:
                                cantidadStock = 0
                                # ? se restan las catidades de ese articulo a cada uno de los diás en los que se usa
                                for d in range(int(demora)):
                                    cantidadStock = cantidadStock + int(self.dictStock[id_plataforma][idArticulo][fechas[fechas.index(fecha) - d]]) - cantidad
                            else:
                                cantidadStock = int(
                                    self.dictStock[id_plataforma][idArticulo][fecha]) - cantidad
                        stock_plat[idArticulo][id_plataforma] = cantidadStock
                        suma_art_plat = suma_art_plat + cantidadStock
                        
                    stocks[idArticulo] = {x:int(y)/suma_art_plat if suma_art_plat > 0 else 0 for x,y in stock_plat[idArticulo].items()}
                # aplanamos el dict para que todos los valores de los articulos en todas las plataformas generen el coste
                counter = collections.Counter()
                for d in stocks.values():
                    counter.update(d)
                stocks = dict(counter)

                fitness_plats = {}
                for id_plataforma in self.ini_sol[id_viaje]:
                    #  Calculos para el coste de transporte normalizado
                    ct = float(self.ini_sol[id_viaje][id_plataforma]['Precio'])
                    ct_all = np.sum([float(f['Precio'])
                                     for f in g.ini_sol[id_viaje].values()])

                    #  Calculos para el coste del stock normalizado
                    cs = stocks[id_plataforma]

                    # Función fitness
                    fitness_plats[id_plataforma] = ct/ct_all + cs
                
                # obtenemos la plataforma con mayor fitness y su valor
                fitness_viajes[id_viaje] = max(fitness_plats.items(), key=operator.itemgetter(1))[0] 
                fitness_valores[id_viaje] = fitness_plats[max(fitness_plats.items(), key=operator.itemgetter(1))[0]]
            
            #evaluacion de los fitnees del lcr
            id_viaje_select = max(fitness_valores.items(), key=operator.itemgetter(1))[0]
            plataforma_viaje_select = fitness_viajes[id_viaje_select]    
            
            list_init = dict(init)
            del list_init[id_viaje_select]
            init = list(list_init.items()) 
            self.solucion[id_viaje_select] = plataforma_viaje_select
        return self.solucion



start_time = time.time()
g = Grasp()
print(g.GRASP_Solution())
print("--- %s seconds ---" % (time.time() - start_time))
