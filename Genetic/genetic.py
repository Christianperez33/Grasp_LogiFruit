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
    print(len(poblacion))
    for i in range(iter):
        ## Obtengo fitness mejor, media fitness y proporcion fitness
        fitness=get_fitness(list_CT)
        self.fitness_Global = fitness[0]
        self.fitness_Best = fitness[1]
        self.list_fitness=fitness[2]
        ## k es un parámetro que establece la "competencia a la hora de elegir un padre" si k es igual a el total de soluciones eligiria siempre los mejores
        #k=int(round(len(poblacion)/3,0))
        k = int(1+((len(poblacion)/(iter)))*(i))
        print((k))
        nueva_generacion=list()
        list_candidatos_CT=list()
        ## Recorro la población dos a dos 
        for j in range(0,self.n_population,2):
            fathers=list()
            ## SELECCION PROGENITORES : Escojo dos padres para la nueva generacion, metodo torneo
            fathers=choose_fathers(self,k)
            ## REPRODUCCION : Metodo para crear nuevos individuos a partir de los progenitores
            family=reproduce(self,fathers,50)
            ## SELECCION NUEVA GENERACION: solo por fitness (AGREGAR EDAAD MÁXIMA)
            candidatos=list()         
            ## Recorro cada miembro de la familia y calculo su coste de transporte.
            for ss in family:
                coste_transporte = 0
                for s in ss:
                    cosas = self.oriViajes[s]['PlataformasPosibles']['CosteTransporte']
                    cosas = cosas if isinstance(cosas, list) else [cosas]
                    for c in cosas:
                        if int(c['Plataforma']) == int(ss[s]):
                            coste_transporte = coste_transporte + float(c['Precio'])
                candidatos.append(coste_transporte/self.n_travel)
            
            ## Ordeno los miembros de la familia por fitness
            lista=numpy.argsort(candidatos)
            ## MUTACION 3% sobre los representantes de la nueva generacion
            rndm_mutate= random.sample(range(1, 100), 2)
            ii=0
            #print(rndm_mutate) 
            for item in rndm_mutate:
                if item<=2:
                    mutation(self,family[lista[ii]])
                ii=ii+1
            #if rndm_mutate<=3:
            #print(rndm_mutate)
            #print(random.randint(0,100))
            #print(candidatos)
            
            #print(lista)
            #os._exit(0)
            nueva_generacion.append(family[lista[0]])
            nueva_generacion.append(family[lista[1]])
            list_candidatos_CT.append(candidatos[lista[0]])
            list_candidatos_CT.append(candidatos[lista[1]])
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
    fitness_best = min(list_CT) 
    fitness_Global = statistics.mean(list_CT)
    suma_fitness=sum(list_CT)
    new_fit = [round((k/suma_fitness),5) for k in list_CT]
    #print (new_fit)
    return(fitness_Global,fitness_best,new_fit)

def choose_fathers(self,k):
    fathers=list()
    sample_tournament=copy.deepcopy(self.list_fitness)
    ##copydeepcopy de fitness
    sampling = random.sample(sample_tournament, k=k)
    best_sample=min(sampling)
    ss=(best_sample)
    res_list = [ii for ii in range(len(self.list_fitness)) if self.list_fitness[ii] == ss]
    fathers.append(res_list[0])
    sample_tournament.remove(best_sample)
    sampling = random.sample(sample_tournament, k=k)
    best_sample=min(sampling)
    ss=(best_sample)
    res_list = [ii for ii in range(len(self.list_fitness)) if self.list_fitness[ii] == ss]
    fathers.append(res_list[0])
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
    list_father=random.sample(list(father),umbral)
    list_mother=list(set(father.keys()) - set(list_father))
    for item in list_father:
        hijo1.append((item,father[item]))
        hijo2.append((item,mother[item]))
    for item in list_mother:
        hijo1.append((item,mother[item]))
        hijo2.append((item,father[item]))
    itemDict = {item[0]: item[1] for item in hijo1}
    family.append(itemDict) 
    itemDict = {item[0]: item[1] for item in hijo2}
    family.append(itemDict) 

    return family

def mutation(self,person):
    #print(person)
    list_father=random.sample(list(person.keys()),1)
    cosas = self.oriViajes[list_father[0]]['PlataformasPosibles']['CosteTransporte']
    cosas = cosas if isinstance(cosas, list) else [cosas]
    viaje_mutar=list_father[0]
    lista_mutar = random.sample(cosas,1)
    plat_mutar = lista_mutar[0]['Plataforma']
    #print(cosas)
    #print(random.sample(cosas,1))
    #print(viaje_mutar)
    #print(lista_mutar)
    #print(plat_mutar)
    #print(person[viaje_mutar])
    person[viaje_mutar]=plat_mutar
    #print(person[viaje_mutar])
    #cosas = self.oriViajes[s]['PlataformasPosibles']['CosteTransporte']
    #os._exit(0)
    return 0