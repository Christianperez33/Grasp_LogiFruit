import time
from grasp import *
import argparse
from tqdm import tqdm
import json
from getData import DatosStock
from getData import DatosViajes
from getData import DatosPrecio
import os
argparser = argparse.ArgumentParser()
argparser.add_argument('-x', '--stock')
argparser.add_argument('-y', '--viajes')
argparser.add_argument('-z', '--precios')
argparser.add_argument('-s', '--solucion')
args = argparser.parse_args()

stock = DatosStock(args.stock)
precios = DatosPrecio(args.precios)
viajes = DatosViajes(args.viajes)

ct = []
cs = {}
f = open(args.solucion, "rb")
sol = json.loads(f.read())
for s in sol:
    cs[s] = []
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
        for f in list(stockitem.keys())[int(plataforma["Demora"])+index_fecha:]:
            resto  = int(stockitem[f]) - int(a["Cantidad"])
            if resto < 0:
                cs[s].append( int(a["Cantidad"])*float(precios.dictPrecios[a['Articulo']]["PrecioUnitario"]))
            stockitem[f] = resto
    
cs_fin = {}
for c in cs:
    cs_fin[c] = np.sum(cs[c])
    

print(np.sum(ct)/len(ct))
print(np.sum(list(cs_fin.values()))/len(ct))

