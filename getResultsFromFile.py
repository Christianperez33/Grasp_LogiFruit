import time
from grasp import *
import argparse
from tqdm import tqdm
import json
from getData import DatosStock
from getData import DatosViajes
from getData import DatosPrecio
import os
import copy
argparser = argparse.ArgumentParser()
argparser.add_argument('-x', '--stock', default="./Genetic/data_grasp/StockSolucionResolver.csv")
argparser.add_argument('-y', '--viajes', default="./Genetic/data_grasp/viajes_zonas.xml" )
argparser.add_argument('-z', '--precios', default="./Genetic/data_grasp/precios.csv")
argparser.add_argument('-d', '--dir')
args = argparser.parse_args()

stockORI = DatosStock(args.stock)
preciosORI = DatosPrecio(args.precios)
viajesORI = DatosViajes(args.viajes)

for filename in os.listdir(args.dir):
    stock = copy.deepcopy(stockORI)
    precios = copy.deepcopy(preciosORI)
    viajes = copy.deepcopy(viajesORI)
    
    ct = []
    cs = {}
    file = open(args.dir+filename, "rb")
    sol = json.loads(file.read())

    for s in sol:
        cs[s] = 0
        if s not in viajes.dictViajes.keys(): continue
        viaje = viajes.dictViajes[s]
        fecha = viaje["FechaDescarga"]
        articulos = viaje["Carga"]["CantidadModelo"] if isinstance(viaje["Carga"]["CantidadModelo"],list) else [viaje["Carga"]["CantidadModelo"]]
        plataformas = viaje["PlataformasPosibles"]["CosteTransporte"] if isinstance(viaje["PlataformasPosibles"]["CosteTransporte"],list) else [viaje["PlataformasPosibles"]["CosteTransporte"]]
        plataforma = [p for p in plataformas if p["Plataforma"] == sol[s]][0]

        ct.append(float(plataforma["Precio"]))
        
        for a in articulos:
            stockitem = stock.dictStock[sol[s]][a['Articulo']]
            index_fecha = [i for i in range(len(stockitem.keys())) if list(stockitem.keys())[i] == fecha][0]
            costearticulo = 0
            for f in list(stockitem.keys())[int(plataforma["Demora"])+index_fecha:]:
                resto  = int(stockitem[f]) - int(a["Cantidad"])
                if resto < 0:
                    costearticulo +=  abs(resto)*float(precios.dictPrecios[a['Articulo']]["PrecioUnitario"])
                stockitem[f] = resto
            cs[s] += costearticulo
    cs_final = int(np.sum(list(cs.values())))

    cstock = str((cs_final/len(cs)))
    ctransporte = str( (np.sum(ct)/len(ct)) )
    ctotal = str( float(cstock) + float(ctransporte))
    print( str(filename)+";"+ctotal+";"+ctransporte+";"+cstock) 