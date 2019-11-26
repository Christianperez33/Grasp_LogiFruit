import datetime
import os
import operator
from getData import DatosStock
from getData import DatosViajes
from collections import OrderedDict
import numpy as np


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
        self.ini_sol = self.getData() # ? dict --> {'idViaje':{ 'idPlataforma':{'Precio': str(float), 'Demora':str}, ...}, ...}

    def getData(self):
        """
        getData Función que preprocesa los datos para su posterior uso

        Returns:
            dict --> {'idViaje':{ 'idPlataforma':{'Precio': str(float), 'Demora':str}, ...}, ...}
        """
        self.dictStock = self.oriStock
        self.dictViajes = self.oriViajes
        output = dict(zip(set(self.dictViajes),[{} for v in set(self.dictViajes)]))
        for viaje in self.dictViajes:

            fecha = self.dictViajes[viaje]['FechaDescarga']

            plataformas = self.dictViajes[viaje]['PlataformasPosibles']['CosteTransporte']
            plataformas = plataformas if isinstance(
                plataformas, list) else [plataformas]

            articulos = self.dictViajes[viaje]['Carga']['CantidadModelo']
            articulos = articulos if isinstance(articulos, list) else [articulos]

            for plataforma in plataformas:
                idPlataforma = plataforma['Plataforma']
                coste = float(plataforma['Precio'])
                demora = plataforma['Demora']
                if len(plataformas) == 1:
                    for articulo in articulos:
                        idArticulo = articulo['Articulo']
                        cantidad = int(articulo['Cantidad'])
                        fechas = list( self.dictStock[idPlataforma][idArticulo].keys())
                        if fecha in fechas :
                            if fechas.index(fecha)-int(demora) > 0:
                                cantidadStock = 0
                                # ? se restan las catidades de ese articulo a cada uno de los diás en los que se usa
                                for d in range(int(demora)):
                                    cantidadStock = cantidadStock + int(self.dictStock[idPlataforma][idArticulo][fechas[fechas.index(fecha) - d]]) - cantidad
                                    self.dictStock[idPlataforma][idArticulo][fechas[fechas.index(fecha)- d ]] = str(cantidadStock)
                            else:
                                cantidadStock = int(self.dictStock[idPlataforma][idArticulo][fecha]) - cantidad
                                self.dictStock[idPlataforma][idArticulo][fecha] = str(cantidadStock)

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
        
        #viajes con cada una de las plataformas
        init = listaLCR[:LCR-1] 
        resto = listaLCR[LCR-1:]
        for val in resto:
            init.append(val)
            fecha = self.dictViajes[val[0]]['FechaDescarga']
            for id_viaje, nplat in init:
                articulos = self.dictViajes[id_viaje]['Carga']['CantidadModelo']
                stocks = []            
                
                #  Calculos para el coste de stock normalizado
                for articulo in articulos:
                    idArticulo = articulo['Articulo']
                    cantidad = int(articulo['Cantidad'])
                    stock_art = {}
                    for id_plataforma in self.ini_sol[id_viaje]:
                        demora = self.ini_sol[id_viaje][id_plataforma]['Demora']
                        fechas = list( self.dictStock[id_plataforma][idArticulo].keys())
                        if fecha in fechas :
                            if fechas.index(fecha)-int(demora) > 0:
                                cantidadStock = 0
                                # ? se restan las catidades de ese articulo a cada uno de los diás en los que se usa
                                for d in range(int(demora)):
                                    cantidadStock = cantidadStock + int(self.dictStock[id_plataforma][idArticulo][fechas[fechas.index(fecha) - d]]) - cantidad
                            else:
                                cantidadStock = int(self.dictStock[id_plataforma][idArticulo][fecha]) - cantidad
                        stock_art[id_plataforma] = cantidadStock
                    
                    diviendo_art = np.sum(stock_art.values())
                    stocks.append({x:y/diviendo_art for x, y in stock_art.items()})
                                
                
                for id_plataforma in self.ini_sol[id_viaje]:
                    #  Calculos para el coste de transporte normalizado
                    ct = float(self.ini_sol[id_viaje][id_plataforma]['Precio'])
                    ct_all = np.sum([float(f['Precio']) for f in g.ini_sol[id_viaje].values()])
                
                    #  Calculos para el coste del stock normalizado
                    cs = stocks[id_plataforma]
                    cs_all = np.sum(stocks.values())
                    
                    # Función fitness
                    fitness =  ct/ct_all + cs/cs_all
                        
                        
                        
                    
                
            del init[-1]
        return []  # self.solucion


g = Grasp()
# print(g.GRASP_Solution())
print(g.solucion)
