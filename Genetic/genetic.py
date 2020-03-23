import os
import json
from operator import itemgetter
from getData import DatosViajes
from getData import DatosPrecio 
import statistics
import random
import csv
import copy
import numpy

class Genetic:
    def __init__(self,viajes ="./data_grasp/viajes_zonas.xml",precios = "./data_grasp/precios.csv"):
        values=getPopulation()
        self.datos = values[0]
        self.n_population=values[1]
        self.n_travel = values[2]
        self.CT = values[3]
        self.viajes = DatosViajes(viajes)
        self.oriViajes = copy.deepcopy(self.viajes.dictViajes)
        self.precios = DatosPrecio(precios)
        self.oriPrecios = copy.deepcopy(self.precios.dictPrecios)

def develope(self,iter):
    poblacion = self.datos
    list_CT = self.CT
    print(self.n_travel) 
    for i in range(iter):
        self.fitness = get_fitness(list_CT)
        #print(self.fitness)
        list_CT2=(self.fitness)
        k=int(round(len(poblacion)/3,0))
        
        nueva_generacion=list()
        list_candidatos_CT=list()
        for j in range(0,self.n_population,2):
            fathers=list()
            fathers=choose_fathers(self,k)
            family=reproduce(self,fathers,50)
            candidatos=list()
                            
            for ss in family:
                coste_transporte = 0
                
                for s in ss:
                    cosas = self.oriViajes[s]['PlataformasPosibles']['CosteTransporte']
                    cosas = cosas if isinstance(cosas, list) else [cosas]
                    for c in cosas:
                        if int(c['Plataforma']) == int(ss[s]):
                            coste_transporte = coste_transporte + float(c['Precio'])
                candidatos.append(coste_transporte/self.n_travel)              
                #print(coste_transporte/self.n_travel)
            #print(sorted(candidatos))
            #print(numpy.argsort(candidatos))
            lista=numpy.argsort(candidatos)
            #print(lista)
            nueva_generacion.append(family[lista[0]])
            nueva_generacion.append(family[lista[1]])
            list_candidatos_CT.append(candidatos[lista[0]])
            list_candidatos_CT.append(candidatos[lista[1]])
            #print(family[1])
        #print(nueva_generacion)
        #
        # 
        #list_CT = [(k, v) for k, v in nueva_generacion]  
        list_CT =  list_candidatos_CT
        self.datos = nueva_generacion
    return list_CT        

def getPopulation():
    list_population = os.listdir(path='./data')
    population = list()
    list_CT = list()
    for json_ in list_population:
        with open('./data/'+json_) as f:
            someone = json.load(f)
            someone = {k: v for k,v in sorted(someone.items(), key=itemgetter(0))}
            list_CT.append(-someone.pop("CT"))  
            population.append(someone)
    n_population=len(population)
    n_travel=len(population[0])
    return (population,n_population,n_travel,list_CT)

def get_fitness(list_CT):
    #print(type(list_CT))
    #list_fitness = [ sub['CT'] for sub in list_CT ]
    fitness_best = min(list_CT) 
    fitness_Global = statistics.mean(list_CT)
    suma_fitness=sum(list_CT)
    new_fit = [round((k/suma_fitness),5) for k in list_CT]
    #print (new_fit)
    return(new_fit)

def choose_fathers(self,k):
    fathers=list()
    sample_tournament=self.fitness
    sampling = random.sample(sample_tournament, k=k)
    best_sample=min(sampling)
    ss=(best_sample)
    res_list = [ii for ii in range(len(self.fitness)) if self.fitness[ii] == ss]
    fathers.append(res_list[0])
    sample_tournament.remove(best_sample)
    sampling = random.sample(sample_tournament, k=k)
    best_sample=min(sampling)
    ss=(best_sample)
    res_list = [ii for ii in range(len(self.fitness)) if self.fitness[ii] == ss]
    fathers.append(res_list[0])
    #while(fathers[0]==fathers[1]):
    #    print("esa")
    #    sampling = random.sample(sample_tournament, k=k)
    #    best_sample=min(sampling)
    #    ss=(best_sample)
    #    res_list = [ii for ii in range(len(self.fitness)) if self.fitness[ii] == ss]
    #    fathers[1]=(res_list[0])
    return fathers
            
def reproduce(self,fathers,point_to_divide):
    family=list()
    hijo1=list()
    hijo2=list()
    father=self.datos[fathers[0]]
    mother=self.datos[fathers[1]]
    family.append(father)
    family.append(mother)
    umbral=int(self.n_travel*(point_to_divide/100))
    aux1 = [(k, v) for k, v in father.items()]
    aux2 = [(k, v) for k, v in mother.items()]

    hijo1=aux1[0:umbral]+aux2[umbral:self.n_travel]
    hijo2=aux2[0:umbral]+aux1[umbral:self.n_travel]
    itemDict = {item[0]: item[1] for item in hijo1}
    family.append(itemDict) 
    itemDict = {item[0]: item[1] for item in hijo2}
    family.append(itemDict) 

    return family