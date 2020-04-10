import datetime
import os
from getData import DatosStock
from getData import DatosViajes
from getData import DatosPrecio
from collections import OrderedDict
from collections import Counter
from operator import itemgetter 
import numpy as np
import collections
import operator
import time
import random
import csv
import copy
import math


class Grasp:
    """
     Clase Grasp contiene los metodos necesarios para la correcta obtención de los datos y su procesado para obtener una solución válida
    """

    def __init__(self, shuffle=True, seed=None, stock="./data/stock.csv", viajes ="./data/viajes.csv", precios = "./data/precio.csv"):
        """
        __init__ Constructor que inicializa las variables de stock y viajes segun las funciones desarrolladas para la obtención de los datos
        """
        self.solucion = dict()
        self.solucion_zonas = []
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
        
        
        output = dict(zip(set(self.dictViajes), [ {} for v in set(self.dictViajes)]))
        for viaje in self.dictViajes:
            fecha = self.dictViajes[viaje]['FechaDescarga']
            if self.dictViajes[viaje]['PlataformasPosibles'] is None: continue
            
            plataformas = self.dictViajes[viaje]['PlataformasPosibles']['CosteTransporte']
            plataformas = plataformas if isinstance( plataformas, list) else [plataformas]

            articulos = self.dictViajes[viaje]['Carga']['CantidadModelo']
            articulos = articulos if isinstance(articulos, list) else [articulos]

            for plataforma in plataformas:
                idPlataforma = plataforma['Plataforma']
                
                coste = float(plataforma['Precio'])
                demora = plataforma['Demora']
                # if len(plataformas) == 1:
                #     for articulo in articulos:
                #         idArticulo = articulo['Articulo']
                #         cantidad = int(articulo['Cantidad'])
                #         fechas = list(self.dictStock[idPlataforma][idArticulo].keys())
                #         ini_rango = (fechas.index(fecha)) - int(demora)
                #         rango = fechas[0 if ini_rango <= 0 else ini_rango:]
                #         for f in rango:
                #             self.dictStock[idPlataforma][idArticulo][f] = int(self.dictStock[idPlataforma][idArticulo][f]) - cantidad
                        

                #     self.solucion[viaje] = plataforma['Plataforma']
                #     self.solucion_zonas = self.solucion_zonas + [(self.dictViajes[viaje]['Zona'],plataforma['Plataforma'])]

                #     del output[viaje]
                # else:
                #     output[viaje][plataforma['Plataforma']] = plataforma
                output[viaje][plataforma['Plataforma']] = plataforma
        return output

    def select_mode(self,mode,listaLCR,beta):
        if mode==1:
            listaLCR2=list()
            listaLCR2 = [(k, v) for k, v in listaLCR.items()]
            listaLCR = sorted(listaLCR2, key = lambda y: (y[1]),reverse=False)
        elif mode==2:
            #Se invierte el nplat por cada viaje apra ordenar de mayor a menor el viaje con 1 plat pasa a ser viaje con 9 plat por lo que se escoge antes
            Keymax = max(listaLCR, key=listaLCR.get) 
            n_plat_max=listaLCR[Keymax]
            listaLCR.update((k,n_plat_max -v) for k, v in listaLCR.items())
            listaLCR2=list()
            listaLCR2_=list()
            listaLCR2 = [(k, v) for k, v in listaLCR.items()]
            listaLCR2_ = [(k, v) for k, v in listaLCR.items()]  
            ii=0
            for x in listaLCR2:
                suma_cantidad = 0
                lista = list(listaLCR2[ii])
                cual=x[0]
                articulos = [self.dictViajes[cual]['Carga']['CantidadModelo']] if type(
                    self.dictViajes[cual]['Carga']['CantidadModelo']) != list else \
                self.dictViajes[cual]['Carga']['CantidadModelo']
                articulos = articulos if isinstance(articulos, list) else [articulos]
                if (len(articulos)==1):
                    suma_cantidad=abs(int(articulos[0]['Cantidad']))
                else:
                    for articulo in articulos:
                        suma_cantidad = suma_cantidad+abs(int(articulo['Cantidad']))
                lista.insert(2,suma_cantidad)
                listaLCR2_[ii]=lista
                ii=ii+1
            listaLCR= sorted(listaLCR2_, key=operator.itemgetter(1,2),reverse=True)
            for x in listaLCR:
                del x[2]
            listaLCR = [tuple(l) for l in listaLCR]

        elif mode==3:
            Keymax = max(listaLCR, key=listaLCR.get) 
            n_plat_max=listaLCR[Keymax]
            listaLCR.update((k, n_plat_max-v) for k, v in listaLCR.items())
            listaLCR2=list()
            listaLCR2 = [(k, v) for k, v in listaLCR.items()]
            listaLCR2_=list()
            listaLCR2_ = [(k, v) for k, v in listaLCR.items()]
            ii=0
            for x in listaLCR2:
                lista = list(listaLCR2[ii])
                cual = x[0]
                plataformas=self.datos[cual]

                if len(plataformas)==1:
                    aux=list(plataformas)[0]
                    suma_demora=abs(int(plataformas[aux]['Demora']))
                else:
                    suma_demora=0
                    for xx in plataformas:
                        suma_demora=suma_demora+int(plataformas[xx]['Demora'])
                lista.insert(2, suma_demora)
                listaLCR2_[ii] = lista
                ii = ii + 1
            
            listaLCR = sorted(listaLCR2_, key=operator.itemgetter(1,2), reverse=True)
            for x in listaLCR:
                del x[2]
            listaLCR = [tuple(l) for l in listaLCR]
        elif mode==4:
            listaLCR2=list()
            listaLCR2 = [(k, v) for k, v in listaLCR.items()]
            listaLCR2_=list()
            listaLCR2_ = [(k, v) for k, v in listaLCR.items()]
            ii=0
            for x in listaLCR2:
                suma_cantidad=0
                lista = list(listaLCR2[ii])
                cual=x[0]
                articulos = [self.dictViajes[cual]['Carga']['CantidadModelo']] if type(
                    self.dictViajes[cual]['Carga']['CantidadModelo']) != list else \
                self.dictViajes[cual]['Carga']['CantidadModelo']
                articulos = articulos if isinstance(articulos, list) else [articulos]
                if (len(articulos)==1):
                    suma_cantidad=abs(int(articulos[0]['Cantidad']))
                else:
                    for articulo in articulos:
                        suma_cantidad = suma_cantidad+abs(int(articulo['Cantidad']))

                plataformas=self.datos[cual]
                if len(plataformas)==1:
                    aux=list(plataformas)[0]
                    suma_demora=abs(int(plataformas[aux]['Demora']))
                else:
                    suma_demora=0
                    for xx in plataformas:
                        suma_demora=suma_demora+int(plataformas[xx]['Demora'])
                
                lista.insert(2,suma_cantidad)
                lista.insert(3,suma_demora)
                listaLCR2_[ii]=lista
                ii=ii+1
            listaLCR = sorted(listaLCR2_, key=operator.itemgetter(3,2),reverse=True)
            for x in listaLCR:
                del x[2]
                del x[2]
            listaLCR = [tuple(l) for l in listaLCR]
        elif mode==5:
            Keymax = max(listaLCR, key=listaLCR.get) 
            n_plat_max=listaLCR[Keymax]
            suma_demora_total=0
            suma_numero_plat_total=0
            listaLCR.update((k, n_plat_max-v) for k, v in listaLCR.items())
            listaLCR2=list()
            listaLCR2 = [(k, v) for k, v in listaLCR.items()]
            listaLCR2_=list()
            listaLCR2_ = [(k, v) for k, v in listaLCR.items()]
            ii=0
            for x in listaLCR2:
                suma_cantidad = 0
                lista = list(listaLCR2[ii])
                cual = x[0]
                articulos = [self.dictViajes[cual]['Carga']['CantidadModelo']] if type(
                    self.dictViajes[cual]['Carga']['CantidadModelo']) != list else \
                self.dictViajes[cual]['Carga']['CantidadModelo']
                articulos = articulos if isinstance(articulos, list) else [articulos]
                plataformas=self.datos[cual]

                if len(plataformas)==1:
                    suma_numero_plat_total=suma_numero_plat_total+1
                    aux=list(plataformas)[0]
                    suma_demora=abs(int(plataformas[aux]['Demora']))
                    suma_demora_total=suma_demora_total+suma_demora
                else:
                    suma_demora=0
                    for xx in plataformas:
                        suma_demora=suma_demora+int(plataformas[xx]['Demora'])
                        suma_numero_plat_total=suma_numero_plat_total+1
                    suma_demora_total=suma_demora_total+suma_demora
                lista.insert(2, suma_demora)
                if (len(articulos)==1):
                    suma_cantidad=abs(int(articulos[0]['Cantidad']))
                else:
                    for articulo in articulos:
                        suma_cantidad = suma_cantidad+abs(int(articulo['Cantidad']))
                lista.insert(3,suma_cantidad)
                listaLCR2_[ii] = lista
                ii = ii + 1
                if (suma_demora_total!=0):
                    sum_aux_d=[[(int(x)/suma_demora_total) if i == 2 else x for i, x in enumerate(y)] for y in listaLCR2_]
                else:
                    sum_aux_d=listaLCR2_
                sum_aux_p=[[(int(x)/suma_numero_plat_total) if i == 1 else x for i, x in enumerate(y)] for y in sum_aux_d]
            for xj in sum_aux_p:
                xj[1]=xj[1]+xj[2]
                del xj[2]
            listaLCR = sorted(sum_aux_p, key=operator.itemgetter(1,2), reverse=True)
            for xj in listaLCR:
                del xj[2]
            listaLCR = [tuple(l) for l in listaLCR]
        elif mode==6:
            Keymax = max(listaLCR, key=listaLCR.get) 
            #print("####")
            n_plat_max=listaLCR[Keymax]
            #print(n_plat_max)
            suma_numero_plat_total=0
            listaLCR.update((k, n_plat_max-v) for k, v in listaLCR.items())
            listaLCR2=list()
            listaLCR2 = [(k, v) for k, v in listaLCR.items()]
            listaLCR2_=list()
            listaLCR2_ = [(k, v) for k, v in listaLCR.items()]
            ii=0
            for x in listaLCR2:

                suma_cantidad = 0
                lista = list(listaLCR2[ii])
                #print(lista)
                cual = x[0]
                articulos = [self.dictViajes[cual]['Carga']['CantidadModelo']] if type(
                    self.dictViajes[cual]['Carga']['CantidadModelo']) != list else \
                self.dictViajes[cual]['Carga']['CantidadModelo']
                articulos = articulos if isinstance(articulos, list) else [articulos]
                plataformas=self.datos[cual]
                suma_demora_total=0
                if len(plataformas)==1:
                    suma_numero_plat_total=suma_numero_plat_total+1
                    aux=list(plataformas)[0]
                    suma_demora=abs(int(plataformas[aux]['Demora']))
                    suma_demora_total=suma_demora_total/n_plat_max
                else:
                    suma_demora=0
                    for xx in plataformas:
                        suma_demora=int(plataformas[xx]['Demora'])
                        suma_numero_plat_total=suma_numero_plat_total+1
                        suma_demora_total=suma_demora_total+suma_demora
                    
                    suma_demora_total=suma_demora_total/n_plat_max
                lista.insert(2, suma_demora_total)
                if (len(articulos)==1):
                    suma_cantidad=abs(int(articulos[0]['Cantidad']))
                else:
                    for articulo in articulos:
                        suma_cantidad = suma_cantidad+abs(int(articulo['Cantidad']))
                
                lista.insert(3,suma_cantidad)
                listaLCR2_[ii] = lista
                ii = ii + 1
            #print(listaLCR2_)
            #os._exit(0)
            #sum_aux_d=[[(int(x)/suma_demora_total) if i == 2 else x for i, x in enumerate(y)] for y in listaLCR2_]
            #sum_aux_p=[[(int(x)/suma_numero_plat_total) if i == 1 else x for i, x in enumerate(y)] for y in sum_aux_d]
            for xj in listaLCR2_:
                xj[1]=xj[1]+(xj[2]*beta)
                del xj[2]

            #print("#######################")
            listaLCR = sorted(listaLCR2_, key=operator.itemgetter(1,2), reverse=True)
            #print(listaLCR)
            #os._exit(0)
            #print(listaLCR)
            #os._exit(0)
            #print(listaLCR)
            for xj in listaLCR:
               del xj[2]
            listaLCR = [tuple(l) for l in listaLCR]
        return (listaLCR)

    def GRASP_Solution(self,mode=2,beta=50,alfa=0.2,LCR=200, iter=0,test=False):

        factor_alfa = (1-alfa)/len(self.datos)
        listaLCR = {s: len(self.datos[s]) for s in self.datos}
        listaLCR = self.select_mode(mode,listaLCR,beta)
        # listaLCR = sorted(listaLCR.items(),
        #                   key=operator.itemgetter(1),
        #                   reverse=False)

        # viajes con cada una de las plataformas
        total_fitness = 0
        while len(listaLCR) > 0 :

            actual = listaLCR[:(math.floor(len(listaLCR)/3))-1]
            #actual = listaLCR[:LCR]
            if len(actual) == 0:
                actual = listaLCR

            fitness_viajes = {}
            fitness_valores = {}
            fitness_plats_precio = {}
            fitness_plats_cantidad = {}
            fitness_transporte = {}
            fitness_completo_precio = {}
            fitness_no_alfa = {}
            scheduler_alfa = {}
            for id_viaje, nplat in actual:
                articulos = [self.dictViajes[id_viaje]['Carga']['CantidadModelo']] if type(self.dictViajes[id_viaje]['Carga']['CantidadModelo']) != list else self.dictViajes[id_viaje]['Carga']['CantidadModelo']
                stocks = {}
                cantidades ={}
                restos = {}
                fecha = self.dictViajes[id_viaje]['FechaDescarga']
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
                        resto_stock = 0
                        # verificamos si es una fecha válida
                        if fecha in fechas:
                            if fechas.index(fecha)-int(demora) > 0:
                                # ? se restan las catidades de ese articulo a cada uno de los dias en los que se usa
                                for d in range(fechas.index(fecha)-int(demora),len(fechas)+1):
                                    resto_unitario =  int(self.dictStock[id_plataforma][idArticulo][fechas[fechas.index(fecha) - d]]) - cantidad
                                    if resto_unitario < 0:
                                        costeStock = costeStock + ( resto_unitario * precio)
                                    resto_stock = resto_stock + resto_unitario
                                resto_stock = (resto_stock/len(range(fechas.index(fecha)-int(demora),len(fechas)+1))) if resto_stock > 0 else 0
                            else:
                                # ? se restan las catidades de ese articulo a cada uno de los dias en los que se usa
                                for d in range(fechas.index(fecha),len(fechas)+1):
                                    resto_unitario =  int(self.dictStock[id_plataforma][idArticulo][fechas[fechas.index(fecha) - d]]) - cantidad
                                    if resto_unitario < 0:
                                        costeStock = costeStock + (resto_unitario * precio)
                                    resto_stock = resto_stock + resto_unitario
                                resto_stock = (resto_stock/len(range(fechas.index(fecha),len(fechas)+1))) if resto_stock > 0 else 0

                        stocks[idArticulo][id_plataforma] = costeStock
                        restos[idArticulo][id_plataforma] = resto_stock
                
                # aplanamos el dict para que todos los valores de los articulos en todas las plataformas generen el coste
                counter = collections.Counter()
                for d in stocks.values():
                    counter.update(d)
                stocks = dict(counter)

                counter = collections.Counter()
                for d in restos.values():
                    counter.update(d)
                restos = dict(counter)

                fitness_plats_precio[id_viaje] = {}
                fitness_plats_cantidad[id_viaje] = {}
                fitness_transporte[id_viaje] = {}
                fitness_completo_precio[id_viaje] = {}
                fitness_no_alfa[id_viaje] = {}
                for id_plataforma in self.datos[id_viaje]:

                    #  Calculos para el coste de transporte 
                    fitness_transporte[id_viaje][id_plataforma] = float(self.datos[id_viaje][id_plataforma]['Precio'])
                    
                    #  Calculos para el coste del stock
                    # Función fitness
                    fitness_plats_precio[id_viaje][id_plataforma] = stocks[id_plataforma]
                    fitness_completo_precio[id_viaje][id_plataforma] = alfa * fitness_transporte[id_viaje][id_plataforma] + (1 - alfa) * fitness_plats_precio[id_viaje][id_plataforma]
                    fitness_no_alfa[id_viaje][id_plataforma] = fitness_transporte[id_viaje][id_plataforma] + fitness_plats_precio[id_viaje][id_plataforma]
                    #  Calculos para la cantidad de stock
                    # Función fitness en el caso de que todas las plataformas tengan stock positivo
                    fitness_plats_cantidad[id_viaje][id_plataforma] = restos[id_plataforma]


                #Obtención del mejor fitness por stock/precio
                
                dict_precios_positivos = {x:y for x,y in fitness_completo_precio[id_viaje].items() if y >= 0}
                if len(dict_precios_positivos) <= 0:
                    #elijo de todos los negativos el mayor, mas cercano a 0
                    id_plataforma_select = max(fitness_completo_precio[id_viaje].items(), key=operator.itemgetter(1))[0]
                else:
                    #de los positivos cojo el menor
                    id_plataforma_select = min(dict_precios_positivos.items(), key=operator.itemgetter(1))[0]
                
                zero_dict = {x:y for x,y in fitness_plats_precio[id_viaje].items() if y == 0 }
                
                #alfa dinámico
                if(len({x:y for x,y in fitness_plats_precio[id_viaje].items() if y >= 0 }) <= len({x:y for x,y in fitness_plats_precio[id_viaje].items() if y < 0 })) :
                    scheduler_alfa[id_viaje] = False
                else:
                    scheduler_alfa[id_viaje] = True

                cantidad_dict = {x:fitness_plats_cantidad[id_viaje][x] for x in zero_dict.keys()}
                precio_dict = {x:fitness_plats_precio[id_viaje][x] for x in zero_dict.keys()}

                # Por cada uno de los precios con 0 calcular el coste del stock y obtener el que mejor indice tenga 
                if len(list(cantidad_dict.items())) != 0 or len(list(precio_dict.items())) != 0:
                    if fitness_plats_precio[id_viaje][id_plataforma_select] == 0 and len(zero_dict) >= 1 and not all([ int(x) <= 0 for x in cantidad_dict.values()]):
                        cantidad_dict = {x:fitness_plats_cantidad[id_viaje][x] for x in zero_dict.keys()}
                        factor=1.0/(sum(cantidad_dict.values()) if sum(precio_dict.values()) != 0 else 1)
                        cantidad_dict = Counter({x:cantidad_dict[x]*factor for x in cantidad_dict.keys()})
                        
                        factor=1.0/ (sum(precio_dict.values()) if sum(precio_dict.values()) != 0 else 1)
                        precio_dict = Counter({x:precio_dict[x]*factor for x in precio_dict.keys()})
                        
                        cantidad_dict.update(precio_dict)
                        cantidad_dict = dict(cantidad_dict)
                        mediana = len(cantidad_dict.items())//2
                        id_plataforma_select = sorted(cantidad_dict.items(),key=operator.itemgetter(1),reverse=False)[mediana][0]
                    else:
                        id_plataforma_select = min(cantidad_dict.items(), key=operator.itemgetter(1))[0]
                
                fitness_valores[id_viaje] = fitness_completo_precio[id_viaje][id_plataforma_select]
                fitness_viajes[id_viaje] = id_plataforma_select                 


            # evaluacion de los fitness del lcr
            id_viaje_select = min(fitness_valores.items(), key=operator.itemgetter(1))[0]
            if scheduler_alfa[id_viaje_select] == True:
                 alfa = alfa + factor_alfa
            else:
                alfa = alfa - factor_alfa
                
            plataforma_viaje_select = fitness_viajes[id_viaje_select]
            total_fitness = total_fitness + fitness_valores[id_viaje_select]
            
            # eliminamos de la lista el viaje que ya hemos adjudicado

            list_listaLCR = dict(listaLCR)
            del list_listaLCR[id_viaje_select]
            listaLCR = list(list_listaLCR.items()) 

            # añadimos a la solcuión el viaje calculado
            self.solucion[id_viaje_select] = plataforma_viaje_select
            self.solucion_zonas = self.solucion_zonas + [(self.dictViajes[id_viaje_select]['Zona'],plataforma_viaje_select)]
            

            
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

        coste_transporte = 0
        for s in self.solucion:
            cosas = self.oriViajes[s]['PlataformasPosibles']['CosteTransporte']
            cosas = cosas if isinstance(cosas, list) else [cosas]
            for c in cosas:
                if int(c['Plataforma']) == int(self.solucion[s]):
                    coste_transporte = coste_transporte + float(c['Precio'])
                    
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
         
        return [self.solucion,  total_fitness/len(self.solucion), coste_transporte/len(self.solucion), alfa, self.solucion_zonas]