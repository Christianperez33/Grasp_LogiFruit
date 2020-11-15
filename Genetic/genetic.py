import os
import json
from operator import itemgetter
from getData import DatosViajes
from getData import DatosPrecio 
from getData import DatosStock
from collections import OrderedDict
import random
import csv
import copy
import numpy
import time
from tqdm import tqdm
import numpy as np

class Genetic:
    def __init__(self,af,viajes ="./data_grasp/5JULIO/viajes.xml",stock="./data_grasp/5JULIO/stock.csv",precios = "./data_grasp/precios.csv", solpath=""):
        self.solpath = solpath
        self.alfa=af
        self.viajes = DatosViajes(viajes)
        self.oriViajes = copy.deepcopy(self.viajes.dictViajes)
        self.dictViajes  = copy.deepcopy(self.oriViajes)
        self.stock = DatosStock(stock)  
        self.oriStock = copy.deepcopy(self.stock.dictStock)
        self.dictStock   = copy.deepcopy(self.oriStock)
        self.precios = DatosPrecio(precios)
        self.oriPrecios = copy.deepcopy(self.precios.dictPrecios)
        values=getPopulation(self,af)
        self.datos = values[0] ## diccionario poblacion donde la clave es el índice de la solucion y el valor otro diccionario con los viajes-plataforma seleccionados
        ## {'Solucion_1': { 'Viaje_0' : 'Plataforma_12' , 'Viaje_1' : 'Plataforma_3'... }, 'Solucion_2' : {'Viaje_0' : 'Plataforma_8' , 'Viaje_1' : 'Plataforma_7'... }}
        self.age=values[1] ## diccionario con las edades de cada miembro de la poblacion
        ## {'Solucion_1':'Edad_ 0',...,'Solucion_N':'Edad_1'}
        self.oriage=copy.deepcopy(self.age)
        self.fitness = values[2] ## diccionario con el fitness de cada miembro de la poblacion
        ## {'Solucion_1':'Fitness_210',...,'Solucion_N':'Fitness_205'}
        suma_fitness=sum(self.fitness.values())
        lista_fitness=[round((k/suma_fitness),5) for k in self.fitness.values()]
        self.list_fitness= {str(x+1) : lista_fitness[x] for x in range(len(lista_fitness))} ## diccionario con la proporcion del fitness en relacion a la suma total (SELECCIÓN MODO TORNEO)
        ## {'Solucion_1':'Fitness_%_0.007',...,'Solucion_N':'Fitness_%_0.0089'}
        self.CT = values[3] ## diccionario con el coste de transporte de cada miembro de la poblacion
        ## {'Solucion_1':'CT_X',...,'Solucion_N':'CT_Y'}
        self.CS = values[4] ## diccionario con el coste de stock de cada miembro de la poblacion
        ## {'Solucion_1':'CS_X',...,'Solucion_N':'CS_Y'}

        
def develope(self,iter,k_mut,k_crossover,alfa,max_age,n_son,n_sup):
    ## Edad máxima individuo en funcion de las iteraciones
    max_age=int((max_age/100)*iter)
    ## Escritura del encabezado del seguimiento del fitness a lo largo de la iteraciones
    with open("./Genetic/results/"+"seguimiento fitness.csv", 'a+',newline='') as csvfile:
        writer = csv.writer(csvfile,delimiter=';')
        writer.writerow(["Iteracion","Fitness global","Mejor fitness","Coste transporte","Coste de stock"])
        # Bucle de las iteraciones del AG
        poblacion = self.datos
        for i in tqdm(range(iter)):
            self.dictStock   = copy.deepcopy(self.oriStock)            

            ## Obtenemos los valores del fitness de la poblacion

            fitness_values=get_fitness(self.fitness,self.CT,self.CS,len(poblacion[list(poblacion.keys())[0]]))
            self.fitness_Global = fitness_values[2] ## Media
            self.fitness_Best = fitness_values[1]   ## Mejor valor 
            self.index_best_fitness=fitness_values[0]   ## Indice mejor valor
            self.list_fitness=fitness_values[3] ## Lista proporcion fitness( torneo)
            
            # create_excel(self,fitness_values[0],poblacion,str(i))
            ## Escribo los resultados para el seguimiento
            writer.writerow([int(i),int(self.fitness_Global),int(self.fitness_Best),int(fitness_values[4]),int(fitness_values[5])])
            #csvfile.close()

            nueva_generacion=list() # Lista donde se almacenenan la asignacion viaje-platafornma de la nueva generacion
            list_new_generation_fitness=list()  # Lista donde se almacenena el fitness de la nueva generacion
            list_new_generation_ct=list()  # Lista donde se almacenena el coste de transporte de la nueva generacion
            list_new_generation_cs=list()  # Lista donde se almacenena el coste de stock de la nueva generacion
            lista_edad=list()  # Lista donde se almacenena la edad de  la nueva generacion

            ## Recorro la población dos a dos 
            par = set(list(poblacion.keys())[::2])
            impar = set(list(poblacion.keys())) - par
            minlen = min((len(par),len(impar)))
            fff = [list(f) for f in zip(list(par)[:minlen],list(impar)[:minlen])]

            for fathers in fff:
                # Variables booleanas para decidir si los padres han alcanzado la edad máxmima
                father_die=False
                mother_die=False
                # # COMPROBACION EDAD MAXIMA: Compruebo en el diccionario de la edad de las soluciones si los padres escogidos han alcanzado la edad maxima
                if self.oriage[str(fathers[0])]>=max_age:
                    father_die=True
                if self.oriage[str(fathers[1])]>=max_age:
                    mother_die=True
                ## REPRODUCCION : Metodo para crear nuevos individuos a partir de los progenitores

                family=reproduce(self,fathers,k_crossover,n_son)
                
                ## SELECCION NUEVA GENERACION: solo por fitness
                fitness_candidatos=list()
                list_cs=list()    
                list_ct=list() 
                ## Recorro cada NUEVO miembro de la familia y calculo el fitness y su coste de TRANSPORTE Y STOCK .
                for member in family:
                    [fitness,ct,cs]=calculate_fitness(self,member,alfa)
                    fitness_candidatos.append(fitness)
                    list_cs.append(cs)
                    list_ct.append(ct)
                    # MUTACION POR CADA MIEMBRO DE LA FAMILIA
                    if k_mut > random.choice(list(range(1,100))):
                        mutation(self,member)
                ## Ordeno los indices de los miembros de la familia por fitness
                lista_indices_candidatos=numpy.argsort(fitness_candidatos)

                # Ejemplo familia con tres hijos [0 1 2 3 4] donde 0 y 1 son los padres con variable "fitness_candidatos" [298 276 250 278 295]
                # Despues de ordenar por fitness , "lista_indices_candidatos" [2 1 3 4 0]
                #EDAD MÁXIMA
                if father_die:
                    lista_indices_candidatos = lista_indices_candidatos[lista_indices_candidatos != 0]
                if mother_die:
                    lista_indices_candidatos = lista_indices_candidatos[lista_indices_candidatos != 1]
                
                ## Por cada miembro que pasa a la nueva generacion construimos los diccionarios correspondientes
                for i_new in range(n_sup):
                    nueva_generacion.append(family[lista_indices_candidatos[i_new]])
                    list_new_generation_fitness.append(fitness_candidatos[lista_indices_candidatos[i_new]])
                    list_new_generation_ct.append(list_ct[lista_indices_candidatos[i_new]])
                    list_new_generation_cs.append(list_cs[lista_indices_candidatos[i_new]])
                    ## Recorro todos los miembros que avanzan de generacion (n_sup) y añado el diccionario de la edad
                    # if lista_indices_candidatos[i_new] >=2: # Si el valor es mayor o igual a dos es un hijo el que avanza de generacion
                    lista_edad.append(0) # Si es un hijo el que avanza de generacion inicializamos la edad a cero
                    # else: # Si el valor es menor a dos es un padre el que avanza de generacion
                    #     lista_edad.append(self.oriage[str(fathers[lista_indices_candidatos[i_new]])]+1) # Busco su edad en el diccionario con la clave que obtenemos de la lista de padres en funcion de que sea 0 (padre) o 1 (madre)
                
            # Una vez acaba la iteracion, actualizamos los valores de la clase GENETIC
            self.datos = {str(x+1) : nueva_generacion[x] for x in range(len(nueva_generacion))} # Actualizo poblacion
            self.oriage = {str(x+1) : lista_edad[x] for x in range(len(lista_edad))} # Actualizo la edad de la poblacion
            self.fitness= {str(x+1) : list_new_generation_fitness[x] for x in range(len(list_new_generation_fitness))} # Actualizo el fitness de la poblacion
            self.CT= {str(x+1) : list_new_generation_ct[x] for x in range(len(list_new_generation_ct))} # Actualizo el coste de transporte de la poblacion
            self.CS= {str(x+1) : list_new_generation_cs[x] for x in range(len(list_new_generation_cs))} # Actualizo el coste de stock de la poblacion
            self.n_population = len(self.datos) # Actualizo el tamaño de la poblacion
            
            print(self.n_population)
            id,xx =min(self.fitness.items(),key=lambda x:x[1])
            print((self.fitness[id],self.CT[id],self.CS[id]))
    return self.fitness,self.datos        

def getPopulation(self,alfa): # Funcion de inicialización de los datos del AG
    
    list_population = os.listdir(path=self.solpath) # PATH donde se alojan las soluciones del GRASP que son la pobalcion inicial del AG
    # Diccionarios con los datos necesarios durante todo el AG
    population = {}
    age = {}
    fitness = {}
    CT = {}
    CS = {}
    i = 0
    for json_ in list_population:
        i += 1
        with open(self.solpath+json_) as f:
            someone = json.load(f) # Cargo una solucion GRASP 
            # someone=  dict(sorted(someone.items(), key=itemgetter(0)))# Ordeno la solucion por IdViaje
            age[str(i)] = 0 # Diccionario con la edad de cada miembro de la pobacion o solucion 
            population[str(i)] = someone # Diccionario con la asignacacion de viajes-plataforma en la solucion
            if i==1:
                self.n_travel = len(population.get("1")) # Inicializacion numero de viajes de las soluciones
            values_fitness = calculate_fitness(self,someone,alfa,True) ## Funcion de calculo del fitness dad una solucion
            fitness[str(i)] = values_fitness[0] # Diccionario con los fitness de cada solucion 
            CT[str(i)] = values_fitness[1] # Diccionario con el coste de transporte de cada solucion
            CS[str(i)] = values_fitness[2] # Diccionario con el coste de stock de cada solucion
    
    plats = {k:[] for k in self.dictViajes.keys()}
    # todas las posibles plataformas para un viaje
    for v in self.dictViajes:
        p = list(self.dictViajes[str(v)]["PlataformasPosibles"].items())[0]
        for xx in ([p[1]] if isinstance(p[1],dict) else p[1]):
            plats[str(v)].append(xx["Plataforma"])
    tamn = list(range(1,len(population)+1))
    
    for n in range(50-len(population)):
        i += 1
        population[str(i)] = population[str(random.choice(tamn))]
        age[str(i)] = 0
        values_fitness = calculate_fitness(self,population[str(i)],alfa) ## Funcion de calculo del fitness dad una solucion
        fitness[str(i)] = values_fitness[0] # Diccionario con los fitness de cada solucion 
        CT[str(i)] = values_fitness[1] # Diccionario con el coste de transporte de cada solucion
        CS[str(i)] = values_fitness[2] # Diccionario con el coste de stock de cada solucion
        
    for n in range(100-len(population)):
        i += 1
        population[str(i)] = {x:random.choice(plats[x]) for x in list(plats.keys())}        
        age[str(i)] = 0
        values_fitness = calculate_fitness(self,population[str(i)],alfa) ## Funcion de calculo del fitness dad una solucion
        fitness[str(i)] = values_fitness[0] # Diccionario con los fitness de cada solucion 
        CT[str(i)] = values_fitness[1] # Diccionario con el coste de transporte de cada solucion
        CS[str(i)] = values_fitness[2] # Diccionario con el coste de stock de cada solucion
    
    # list_poolsol = os.listdir("./Genetic/poolsol/")
    # for json_ in list_poolsol:
    #     i += 1
    #     with open("./Genetic/poolsol/"+json_) as f:
    #         someone = json.load(f) # Cargo una solucion GRASP 
    #         # someone=  dict(sorted(someone.items(), key=itemgetter(0)))# Ordeno la solucion por IdViaje
    #         age[str(i)] = 0 # Diccionario con la edad de cada miembro de la pobacion o solucion 
    #         population[str(i)] = someone # Diccionario con la asignacacion de viajes-plataforma en la solucion
    #         values_fitness = calculate_fitness(self,someone,alfa,True) ## Funcion de calculo del fitness dad una solucion
    #         fitness[str(i)] = values_fitness[0] # Diccionario con los fitness de cada solucion 
    #         CT[str(i)] = values_fitness[1] # Diccionario con el coste de transporte de cada solucion
    #         CS[str(i)] = values_fitness[2] # Diccionario con el coste de stock de cada solucion
            
    self.n_population = len(population) # Inicializacion numero de miembros de la poblacion inicial
    # print(self.n_population)
    return (population,age,fitness,CT,CS)


def get_fitness(dict_fitness,dict_CT,dict_CS,lensol):
    fit = {id: dict_CT[id]+(dict_CS[id]/lensol)  for id in dict_fitness}
    index_fitness_best = min(fit, key=fit.get) # Indice mejor fitness de las soluciones
    fitness_Global = np.mean(list(fit.values())) # Media del fitness de la poblacion
    suma_fitness=sum(fit.values()) # Suma del fitness de la poblacion
    lista_fitness = [round((k/suma_fitness),5) for k in fit.values()] # Proporcion del fitness en función de la suma global
    lista_fitness= {str(x+1) : lista_fitness[x] for x in range(len(lista_fitness))} 
    fitness_best=fit.get(index_fitness_best) # Valor mejor fitness  
    CT_best=dict_CT.get(index_fitness_best) # Mejor coste de transporte
    CS_best=dict_CS.get(index_fitness_best) # Mejor coste de stock

    return(index_fitness_best,fitness_best,fitness_Global,lista_fitness,CT_best,CS_best)

def choose_fathers(self,k): # Funcion de seleccion de los padres de la pobalcion que generan nueva descendencia
    fathers=list() # Inicializo la lista a añadir los indices de los padres escogidos
    list_fitness=list(self.list_fitness.values()) # Inicializo la lista con las proporciones de los fitness
    sample_tournament=copy.deepcopy(list_fitness)
  
    ## SELECCION PADRE
    # De la lista de proporciones de fitnees de los individuos escojo  "k" miembros aleatoriamente para obtener el mejor
    sampling = random.sample(sample_tournament, k=k)
    # De esa lista de k miembros escogidos aleaoriamente obtenemos el mejor
    best_sample=min(sampling)
    res_list = [ii for ii in range(len(list_fitness)) if list_fitness[ii] == best_sample]
    fathers.append(res_list[0]+1)
    ## Eliminamos de la lista de miembros al padre
    sample_tournament.remove(best_sample)

    ## SELECCION MADRE
    sampling = random.sample(sample_tournament, k=k)
    best_sample=min(sampling)
    res_list = [ii for ii in range(len(list_fitness)) if list_fitness[ii] == best_sample]

    fathers.append(res_list[0]+ 1)
    return fathers
            
def reproduce(self,fathers,point_to_divide,n_son): # Funcion que obtiene nueva descendencia a partir de los padres escogidas en la funcion anterior
    family=list() # Lista donde almaceno la familia
    father=self.datos[str(fathers[0])] # Obtengo el indice de la solucion del padre
    mother=self.datos[str(fathers[1])] # Obtengo el indice de la solucion de la madre

    family.append(father) # Actualizo la familia con el padre
    family.append(mother) # Actualizo la familia con la madre
    umbral=int(self.n_travel*(point_to_divide/100)) # Variable con el % de viajes que se cruzan en la nueva descendencia de padre-madre
    ## Bucle por cada hijo de la nueva generacion
    for i in range(n_son):
        hijo={} # Lista donde almaceno los hijos
        list_father=random.sample(list(father),umbral) # Obtengo de manera aleatoria "umbral%" de los viajes del padre
        list_mother=list(set(father.keys()) - set(list_father))# Obtengo el resto de viajes de la madre
        # for item in list_father: # Añado los viajes-plataforma del padre
        #     hijo.append((item,father[item]))
        # for item in list_mother: # Añado los viajes-plataforma de la madre
        #     hijo.append((item,mother[item]))
        # itemDict = {item[0]: item[1] for item in hijo} # Lo convierto en un diccionario
        hijo.update({i:father[i] for i in list_father})
        hijo.update({i:mother[i] for i in list_mother})
        
        family.append(hijo) 

    return family

def mutation(self,person):  # funcion mutation a partir de un miembro de la familia, escoge un viaje para cambiar su plataforma asignada
    viaje_mut=random.sample(list(person.keys()),1) # Escoge aleatoriamente un viaje a mutar
    viaje_mutar=viaje_mut[0]
    # Obtenemos las plataformas disponibles
    cosas = self.oriViajes[viaje_mutar]['PlataformasPosibles']['CosteTransporte']
    cosas = cosas if isinstance(cosas, list) else [cosas]

    # Si el viaje que muta solo tiene una plataforma disponible no tiene sentido mutar ese viaje ya que no varia el inidividuo
    while (len(cosas)==1):
        viaje_mut=random.sample(list(person.keys()),1) # Escoge aleatoriamente otro viaje a mutar
        viaje_mutar=viaje_mut[0]
        # Obtenemos las plataformas disponibles
        cosas = self.oriViajes[viaje_mutar]['PlataformasPosibles']['CosteTransporte']
        cosas = cosas if isinstance(cosas, list) else [cosas]
    
    plataforma_asignada_viaje_mut=person.get(viaje_mutar) # Obtenemos plataforma asignada al viaje a mutar
    plataforma_mut = random.sample(cosas,1) # Escoge aleatoriamente una plataforma a la que mutar

    # Nos aseguramos que la plataforma escogida no es la que ya tenia previamente asignada el viaje, asi no tendia sentido la mutacion
    while plataforma_asignada_viaje_mut==plataforma_mut:
        plataforma_mut = random.sample(cosas,1)

    plat_mutar_asignada = plataforma_mut[0]['Plataforma'] # Obtenemos del diccionario el numero de plataforma
    person[viaje_mutar]=plat_mutar_asignada # Asignamos al miembro de la familia la nueva paltaforma en el viaje esocgido para la mutacion 

    return 0

def calculate_fitness(self,member,alfa,init=False): # Esta función calcula la formula del fitness para una solucion, dado un alfa con el que realizar el calculo con coste de transporte(CT) y coste de stock (CS)
    ## FORMULA FITNESS: (ALFA * CT)  + ((1-ALFA) * CS)
    ## CT-> Coste de transporte, para cda viaje sumar el coste de transporte de su plataforma asignada
    # if init:
    self.dictStock  = copy.deepcopy(self.oriStock)
    coste_transporte = 0
    for s in member:
        cosas = self.oriViajes[s]['PlataformasPosibles']['CosteTransporte']
        cosas = cosas if isinstance(cosas, list) else [cosas]
        for c in cosas:
            if int(c['Plataforma']) == int(member[s]):
                coste_transporte += float(c['Precio'])
    
    ## CS-> Coste de stock, recorremos todos los viajes plataforma de la solucion, comprobando si el stock de las plataformas es negativo y sumando el coste de reponer ese stock
    coste_stock={}

    for id_viaje,id_plat in member.items():
        articulos = [self.dictViajes[id_viaje]['Carga']['CantidadModelo']] if not isinstance(self.dictViajes[id_viaje]['Carga']['CantidadModelo'], list) else self.dictViajes[id_viaje]['Carga']['CantidadModelo']

        stocks = {}
        cantidades = {}
        fecha = self.dictViajes[id_viaje]['FechaDescarga']
        ## Es necesario obtener la demora de la plataforma para el viaje estudiado
        plataformas = self.oriViajes[id_viaje]['PlataformasPosibles']['CosteTransporte']
        plataformas = plataformas if isinstance(plataformas, list) else [plataformas]
       
        demora = [p["Demora"] for p in plataformas if str(p['Plataforma']) == str(id_plat)][0]

        ## Recorremos los articulos de cada viaje   
        for articulo in articulos:
            idArticulo = articulo['Articulo']
            cantidad = abs(int(articulo['Cantidad']))
            precio = self.oriPrecios[idArticulo]["PrecioUnitario"]
            cantidades[idArticulo] = {}
            ## Obtenemos las fechas del diccionario de stock para cruzar con las fechas del viaje y su demora
            fechas = list(self.dictStock[id_plat][idArticulo].keys())
            coste_stock_aux = 0

            init =fechas.index(fecha)-int(demora) if fechas.index(fecha)-int(demora) > 0 else fechas.index(fecha)

            # ? se restan las catidades de ese articulo a cada uno de los dias en los que se usa
            for d in range(init,len(fechas)+1):
                resto_unitario =  int(self.dictStock[id_plat][idArticulo][fechas[fechas.index(fecha) - d]]) - cantidad
                coste_stock_aux += (abs(resto_unitario) * precio if resto_unitario < 0 else 0)
                # self.dictStock[id_plat][idArticulo][fechas[fechas.index(fecha) - d]] = resto_unitario

            stocks[idArticulo] = coste_stock_aux

        coste_stock[id_viaje] = sum(stocks.values())
    # Función fitness
    fitness_completo_precio= ((alfa/100) * coste_transporte/len(member)) + ((1 - (alfa/100)) * (sum(coste_stock.values())/len(coste_stock)))
    # fitness_completo_precio=  coste_transporte + coste_stock/self.n_travel
    return ((fitness_completo_precio),(coste_transporte/len(member)),(sum(coste_stock.values())/len(coste_stock)))

def get_best_solution(list_proportion_fitness): # Funcion que obtiene el indice del miembro de la poblacion con mejor fitness
    return(list_proportion_fitness.index(min(list_proportion_fitness)))

def create_excel(self,index,populate,index_solution):
    # print(type(index))
    # print(type(list(populate.keys())[0]))
    # print(populate[index].items())
    # os._exit(0)
    for id_viaje_select,plataforma_viaje_select in populate[index].items():
        articulos = self.oriViajes[plataforma_viaje_select]['Carga']['CantidadModelo']
        articulos = articulos if isinstance(articulos, list) else [articulos]
        for articulo in articulos:
            idArticulo = articulo['Articulo']
            cantidad = abs(int(articulo['Cantidad']))
            fecha = self.dictViajes[id_viaje_select]['FechaDescarga']
            fechas = list(self.dictStock[plataforma_viaje_select][idArticulo].keys())
            
            # obtenemos la demora de las plataformas 
            plataformas = self.oriViajes[id_viaje_select]['PlataformasPosibles']['CosteTransporte']
            plataformas = plataformas if isinstance(plataformas, list) else [plataformas]
            for plataforma in plataformas:
                if str(plataforma['Plataforma']) == str(plataforma_viaje_select):
                    demora = plataforma['Demora']
                    break

            ini_rango = (fechas.index(fecha)) - int(demora)
            rango = fechas[0 if ini_rango <= 0 else ini_rango:]
            for f in rango:
                self.dictStock[plataforma_viaje_select][idArticulo][f] = int(self.dictStock[plataforma_viaje_select][idArticulo][f]) - cantidad

    # guardamos el diccionario de stock para poder ver el balanceo
    # dictstock = dict(OrderedDict(sorted(self.dictStock.items(), key = lambda t: int(t[0]))))
    with open("./Genetic/results/results_stock/"+"stock_sol_"+index_solution+"+.csv", 'w',newline='') as csvfile:
        writer = csv.writer(csvfile,delimiter=';')
        cuantos_articulos_negativos = 0
        articulo_minimo = 0
        suma_articulos_negativos = 0
        for p in self.dictStock:
            writer.writerow([int(p),' ',' ',' ',' ',' ',' ',' ',' '])
            writer.writerow([' ']+fechas)
            for a in self.dictStock[p]:
                test_list = list(map(int, list(self.dictStock[p][a].values())))
                neg_count = len(list(filter(lambda x: (x < 0), test_list)))
                cuantos_articulos_negativos=cuantos_articulos_negativos+neg_count
                if (neg_count>0):
                    neg_nos = list(filter(lambda x: (x < 0), test_list))
                    suma_articulos_negativos=suma_articulos_negativos+sum(neg_nos)
                if (min(test_list)<articulo_minimo):
                    articulo_minimo=min(test_list)

                writer.writerow([int(a)]+list(self.dictStock[p][a].values()))
            writer.writerow([' '])