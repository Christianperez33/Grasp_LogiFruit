import time
from pprint import pprint
from GRASP.grasp import *
import argparse
from tqdm import tqdm
import json
from Genetic.getData import DatosStock
from Genetic.getData import DatosViajes
from Genetic.getData import DatosPrecio
import os
import copy
import torch
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

def getPlatPrima(member,alfa,n_travel): # Esta función calcula la formula del fitness para una solucion, dado un alfa con el que realizar el calculo con coste de transporte(CT) y coste de stock (CS)
    ## FORMULA FITNESS: (ALFA * CT)  + ((1-ALFA) * CS)
    ## CT-> Coste de transporte, para cda viaje sumar el coste de transporte de su plataforma asignada
    # coste_transporte = 0
    # for s in member:
    #     cosas = oriViajes[s]['PlataformasPosibles']['CosteTransporte']
    #     cosas = cosas if isinstance(cosas, list) else [cosas]
    #     for c in cosas:
    #         if int(c['Plataforma']) == int(member[s]):
    #             coste_transporte = coste_transporte + float(c['Precio'])
    ## CS-> Coste de stock, recorremos todos los viajes plataforma de la solucion, comprobando si el stock de las plataformas es negativo y sumando el coste de reponer ese stock
    # coste_stock=0
    res = {}
    plats = []
    precios_sol=[]
    for id_viaje,id_plat in member.items():
        plats.append(int(id_plat)-1)
        dictStock  = copy.deepcopy(oriStock)
        articulos = [dictViajes[id_viaje]['Carga']['CantidadModelo']] if not isinstance(dictViajes[id_viaje]['Carga']['CantidadModelo'], list) else dictViajes[id_viaje]['Carga']['CantidadModelo']

        # stocks = {}
        # cantidades = {}
        fecha = dictViajes[id_viaje]['FechaDescarga']
        ## Es necesario obtener la demora de la plataforma para el viaje estudiado
        plataformas = oriViajes[id_viaje]['PlataformasPosibles']['CosteTransporte']
        plataformas = plataformas if isinstance(plataformas, list) else [plataformas]
        demora = [p["Demora"] for p in plataformas if str(p['Plataforma']) == str(id_plat)][0]
        precio = np.zeros(14)
        for p in plataformas:
            precio[int(p['Plataforma'])-1] = float(p['Precio'])
        precios_sol.append(precio)
        ## Recorremos los articulos de cada viaje   
        for articulo in articulos:
            idArticulo = articulo['Articulo']
            cantidad = abs(int(articulo['Cantidad']))
            # precio = oriPrecios[idArticulo]["PrecioUnitario"]
            # cantidades[idArticulo] = {}
            ## Obtenemos las fechas del diccionario de stock para cruzar con las fechas del viaje y su demora
            fechas = list(dictStock[id_plat][idArticulo].keys())
            # coste_stock_aux = 0

            init =fechas.index(fecha)-int(demora) if fechas.index(fecha)-int(demora) > 0 else fechas.index(fecha)

            # ? se restan las catidades de ese articulo a cada uno de los dias en los que se usa
            for d in range(init,len(fechas)+1):
                for plat_in in list(dictStock.keys()):
                    resto_unitario =  int(dictStock[plat_in][idArticulo][fechas[fechas.index(fecha) - d]]) - cantidad
                    # coste_stock_aux += (abs(resto_unitario) * precio if resto_unitario < 0 else 0)
                    dictStock[plat_in][idArticulo][fechas[fechas.index(fecha) - d]] = resto_unitario

            # stocks[idArticulo] = coste_stock_aux
        res[id_viaje] = dictStock
        # coste_stock +=  abs(sum(stocks.values()))
    return [res,plats,precios_sol]
    # Función fitness
    # fitness_completo_precio= ((alfa/100) * coste_transporte) + ((1 - (alfa/100)) * (coste_stock))
    # fitness_completo_precio=  coste_transporte + coste_stock/n_travel
    # return ((fitness_completo_precio),(coste_transporte/n_travel),coste_stock)
R_Fin=np.array([])
Label_sol_Fin=np.array([])
Precios_sol_Fin=np.array([])
idx=0
for filename in os.listdir(args.dir):
    idx+=1
    dictStock  = copy.deepcopy(oriStock)
    file = open(args.dir+filename, "rb")
    sol = json.loads(file.read())
    w = copy.deepcopy(oriStock)
    w = {k:{x:list(map(int,list(w[k][x].values())))+[0] for x in w[k]} for k in w}
    w_ini = np.stack([list(w[i].values()) for i in w])

    w_prima_order,plats,precios_sol = getPlatPrima(sol,90,len(sol))
    res_w_prima= {order:{k:{x:list(map(int, list(w_prima_order[order][k][x].values()))) + [0] for x in  w_prima_order[order][k]} for k in  w_prima_order[order]} for order in w_prima_order}

    label_sol = [int(sol[order])-1 for order in w_prima_order]
    w_prima = np.stack([np.stack([list(res_w_prima[o][i].values()) for i in res_w_prima[o]]) for o in res_w_prima])
    
    R=[]
    w_last=w_ini
    for w_i,p in list(zip(w_prima,plats)):
        r_i=w_i-w_last
        r_i = np.multiply([[[x['PrecioUnitario']] for x in precios.dictPrecios.values()]]*14,r_i)
        R.append(np.concatenate((w_i,r_i),axis=2))
        w_last[p]=w_i[p]

    R=np.array(R)
    
    if len(R_Fin)==0:
        R_Fin=R
        Label_sol_Fin=np.array(label_sol)
        Precios_sol_Fin=np.array(precios_sol)
    else:
        R_Fin = np.concatenate((R_Fin, R))
        Label_sol_Fin = np.concatenate((Label_sol_Fin, np.array(label_sol)))
        Precios_sol_Fin = np.concatenate((Precios_sol_Fin, np.array(precios_sol)))

tr_conv_name="TrainingJBNN/train_conv.npy"
tr_lab_name="TrainingJBNN/train_label.npy"
tr_data_name="TrainingJBNN/train_data.npy"
    
np.save(tr_conv_name,torch.tensor(R_Fin,dtype=torch.float))
np.save(tr_lab_name,torch.tensor(Label_sol_Fin))
np.save(tr_data_name,torch.tensor(Precios_sol_Fin,dtype=torch.float))

