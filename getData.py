import xmltodict
import json
import numpy as np
import pandas as pd
import csv 

class DatosViajes:
    def __init__(self,path):
        file = open(path,"r") 
        json_orig = xmltodict.parse(file.read())["ArrayOfViajesLite"]
        json_viajes = json_orig["ViajesLite"]
        self.listaViajes = json_viajes
        self.dictViajes = {str( v['Id'] ): json.loads(json.dumps(v)) for v in json_viajes}
        self.formatFecha()
        file.close()

    def formatFecha(self):
        for key in self.dictViajes:
            fecha = self.dictViajes[key]['FechaDescarga'].split('T')[0]
            fecha = fecha.split('-')
            self.dictViajes[key]['FechaDescarga'] = fecha[2]+'/'+fecha[1]+'/'+fecha[0]
        
    def getIds(self):
        return [viaje["Id"] for viaje in self.listaViajes]

class DatosStock:
    def __init__(self,path):
        data = pd.read_csv(path,sep=';',engine="python", header=None,names=['id','lunes', 'martes', 'miercoles', 'jueves','viernes','sabado','domingo','out'])
        self.csv = data
        self.dictStock = self.getDict()
        self.idsPlataforma = self.getIdsPlataformas()
        self.idsPedidos = self.getIdsPedidos()
    
    def getTableById(self,id,colini=None,colend=None):
        if(colini is None and colend is None):
            return dict(self.csv.loc[id,"id":"domingo"])
        elif(colini is None):
            return dict(self.csv.loc[id,colini])
        else:
            return dict(self.csv.loc[id,colini:colend])
    
    def getIdsPedidos(self):
        array = np.array(self.csv.iloc[:,0])
        array = array[np.logical_not(np.isnan(array))]
        array = np.unique(array[2:]).astype(int)
        return array
    
    def getIdsPlataformas(self):
        return list(self.dictStock.keys())
    
    def getDict(self):
        res = {}
        fechas = ['lunes', 'martes', 'miercoles', 'jueves','viernes','sabado','domingo']
        for id in range(len(self.csv)):
            data = self.csv.iloc[id,:]
            toadm = list(data)
            baseid = toadm[0]
            resto = toadm[1:-1]
            if str(baseid) != "nan":
                if all([str(x) == "nan" for x in resto]) :
                   res[str(int(baseid))] = {}
                   lastId = int(baseid)
                else:
                    res[str(lastId)][str(int(baseid))] = dict(zip(fechas,toadm[1:-1]))
            else:
                fechas = toadm[1:-1]
                
                
        return res



   
# s = DatosStock("data/stock.csv")
# print(s.dictStock['1'])
# v = DatosViajes("data/viajes.xml")
# print(v.dictViajes["2150"])  
