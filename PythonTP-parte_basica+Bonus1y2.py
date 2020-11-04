"""
Created on Wed Oct 28 00:04:13 2020

@author: Raul A. Gutierrez - Programacion Concurrente
"""

import threading
import time
import logging
import random

logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(threadName)s] - %(message)s', datefmt='%H:%M:%S', level=logging.INFO)

cantidadMaxBotellas = 10
cantidadMaxLatas = 15
semaforo = threading.Semaphore(1) # máximo 1 es por la cantidad al mismo tiempo

def generarNumeroEntre(n,m):
    return random.randint(n,m)

def timmer(n,m):
    time.sleep(generarNumeroEntre(n,m))



class Heladera:
    global cantidadMaxBotellas,cantidadMaxLatas
    
    def __init__(self,nombre,botellas = 0,latas = 0,estaEnchufada = False):
        self.nombre = nombre
        self.botellas = botellas
        self.latas = latas
        self.estaEnchufada = estaEnchufada
        
    def agregarBotella(self):
        self.botellas += 1
        logging.info(f'{self.nombre}-> botella ingresada')
    
    def agregarLata(self):
        self.latas += 1
        logging.info(f'{self.nombre}-> lata ingresada')
          
    def estaLlena(self):
        return (self.botellas == cantidadMaxBotellas) and (self.latas == cantidadMaxLatas)
    
    def tieneCervezas(self):
        return (self.botellas != 0) or (self.latas != 0)
    
    def enchufar(self):
        self.estaEnchufada = True    
        
    def tieneLatas(self):
        return (self.latas != 0)
        
    def quitarLata(self):
        self.latas -=1
      
  
    
class Proveedor(threading.Thread):
    global cantidadMaxBotellas,cantidadMaxLatas
    def __init__(self,nombre,proveeBotellas,proveeLatas,monitor,listaHeladeras,llegada):
        super().__init__()
        self.name = nombre
        self.proveeBotellas = proveeBotellas
        self.proveeLatas = proveeLatas
        self.monitor = monitor
        self.listaHeladeras = listaHeladeras
        self.llegada = llegada
        
    def entregaBotella(self):
        self.proveeBotellas -= 1
        logging.info(f'botella entregada, quedan {self.proveeBotellas}')
        #time.sleep(4)
        
    def entregaLata(self):
        self.proveeLatas -= 1
        logging.info(f'lata entregada, quedan {self.proveeLatas}')
        #time.sleep(4)
           
    def entregaCompleta(self):
        return (self.proveeBotellas == 0) and (self.proveeLatas == 0)
    
    def entregarBotellas(self,heladera):
        while (heladera.botellas < cantidadMaxBotellas and self.proveeBotellas > 0):
            self.entregaBotella()
            heladera.agregarBotella()
            time.sleep(2)
            
    def entregarLatas(self,heladera):
        while (heladera.latas < cantidadMaxLatas and self.proveeLatas > 0):
            self.entregaLata()
            heladera.agregarLata()
            time.sleep(2)
    
    def run(self):
        
        time.sleep(self.llegada) # tiempo de llegada del proveedor

        while (True): 
        
            #with self.monitor:  ## Sincroniza para no pizarse con otro proveedor
            
                indice = 0
                #for heladera in self.listaHeladeras: ## recorre la lista de heladeras
                while not self.entregaCompleta() and indice < len(self.listaHeladeras): # otra forma de recorrer las heladeras
                    
                        heladera = self.listaHeladeras[indice]
                        
                        with self.monitor:  ## Sincroniza para no pizarse con otro proveedor
       
                            if not heladera.estaLlena():
                                logging.info(f'la heladera {heladera.nombre} esta enchufada')
                                logging.info(f'la heladera {heladera.nombre} tiene {heladera.botellas} botellas')
                                logging.info(f'la heladera {heladera.nombre} tiene {heladera.latas} latas')
                                logging.info(f'el proveedor {self.name} tiene {self.proveeBotellas} botellas')
                                logging.info(f'el proveedor {self.name} tiene {self.proveeLatas} latas')
                                time.sleep(2)
                                self.entregarBotellas(heladera)
                                self.entregarLatas(heladera)
                            else:
                                self.monitor.notify()
                                logging.info(f'El proveedor {self.name} no entrega, la heladera {heladera.nombre} esta llena')
                                time.sleep(4)
                        
                        if self.entregaCompleta():
                            logging.info(f'El proveedor {self.name} entrego todo')
                            time.sleep(4)
                        
                        #while not heladera.estaLlena():   # mientras esta heladera no esta llena
                            #self.monitor.wait()     # el proveedor quedara a la espera de que el bar le avise que puede seguir con la proxima heladera
            
                        indice +=1
                        time.sleep(4)
                                
                """
                if self.entregaCompleta():  # si el proveedor termina de entregar todos los productos
                    logging.info(f'Se termino la entrega de producto')
                    time.sleep(4)
                    break  # se termina su trabajo"""
                    


def bar(monitorProvee,monitorBeodxs,listaHeladeras):
    global cantidadMaxBotellas, cantidadMaxLatas
    
    logging.info(f'Comienza la fiesta')
    logging.info(f'controlemos las heladeras')
    time.sleep(4)
    
    while (True):       
            
            for heladera in listaHeladeras: ## recorre la lista de heladeras
                
                # La idea es si no esta enchufada la heladera, la enchufamos.
                if not heladera.estaEnchufada:
                    logging.info(f'la heladera {heladera.nombre} tiene timer colocado para enchufar')
                    timmer(3,9) # ponemos un timmer para enchufar
                    heladera.enchufar()
                    
                else:
              
                    with monitorProvee:
                        
                        if heladera.estaLlena(): # si esta llena, informamos la cantidad de botellas y latas que tiene
                            
                            pinchadura(listaHeladeras)
                            
                            logging.info(f'{heladera.nombre} quedo {heladera.botellas} botellas')
                            logging.info(f'{heladera.nombre} quedo {heladera.latas} latas')
                            logging.info(f'la heladera {heladera.nombre} Llena -> boton de enfriando')
                            monitorProvee.notify()  # avisamos al proveveedor colgado que puede seguir entregando
                            time.sleep(5)                               
       
                        else: # si NO esta llena, informamos la cantidad final de botellas y latas 
                            logging.info(f'la heladera {heladera.nombre} no esta llena')
                            logging.info(f'{heladera.nombre} tiene {heladera.botellas} botellas')
                            logging.info(f'{heladera.nombre} tiene {heladera.latas} latas')
                            time.sleep(5)
                            
                    if heladera.tieneCervezas(): # si la heladera tiene cervezas
                        
                            pinchadura(listaHeladeras)
                        
                            with monitorBeodxs: 
                                logging.info(f'la heladera {heladera.nombre} tiene cervezas')
                                logging.info(f'{heladera.nombre} tiene {heladera.botellas} botellas')
                                logging.info(f'{heladera.nombre} tiene {heladera.latas} latas')
                                monitorBeodxs.notify()
                                time.sleep(5)
                            
                            

def pinchadura(listaHeladeras):   
    global cantidadMaxBotellas, cantidadMaxLatas

    numeroAzar = generarNumeroEntre(0,9)
    
    if numeroAzar < 3:  # posibilidades de que se pinche una lata
        
        indice =generarNumeroEntre(0,len(listaHeladeras)-1)
        heladera = listaHeladeras[indice]
        if heladera.tieneLatas():
            logging.info(f'la heladera {heladera.nombre}-> tiene una lata pinchada')
            time.sleep(4)
            #with monitor:  # no necesita monitor, ya que la funcion se llama de del adquire del monitor de la fiesta
            heladera.quitarLata()
            logging.info(f'la heladera {heladera.nombre}-> se quita la lata pinchada')
            time.sleep(4)
                    


class Beodxs(threading.Thread):
    def __init__(self,nombre,botellas,latas,monitor,listaHeladeras):
        super().__init__()
        self.name = nombre
        self.botellas = botellas
        self.latas = latas
        self.monitor = monitor
        self.listaHeladeras = listaHeladeras
        
    def tomarBotella(self):
        self.botellas -= 1
        logging.info(f'Beode {self.name} botella tomada, le quedan por tomar {self.botellas}')
        
    def tomarLata(self):
        self.latas -= 1
        logging.info(f'Beode {self.name} lata tomada, le quedan por tomar {self.latas}') 
        
    def llegoAlLimite(self):
        return (self.botellas == 0) and (self.latas == 0)
    
    def tomaDeBotella(self): 
        return self.botellas != 0
    
    def tomaDeLata(self): 
        return self.latas != 0
    
    def tomaDeAmbos(self):
        return self.tomaDeBotella() and self.tomaDeLata()
    
    def hayaAlgoQueMeGusta(self,heladera):
        return self.tomaDeBotella() or self.tomaDeLata() or self.tomaDeAmbos()
    
    def tomarUnaCerveza(self):
        opcion = random.choice([1,2])
        if self.tomaDeAmbos():
            if opcion == 1:
                self.tomarBotella()
            else:
                self.tomarLata()
        elif self.tomaDeBotella():
            self.tomarBotella()
        else: self.tomarLata()
    
    def run(self):
        timmer(1,9) # Beode desesperado por arrancar a tomar. Lo ponemos a esperar un poco
        
        while not self.llegoAlLimite():
                
                indice =generarNumeroEntre(0,len(self.listaHeladeras)-1)
                heladera = self.listaHeladeras[indice]
                # sincronizamos el acceso a la heladera
                with self.monitor:
                    while not self.hayaAlgoQueMeGusta(heladera) and not heladera.estaLlena() or not heladera.tieneCervezas() or not heladera.estaEnchufada: # mientras no haya cervezas
                        self.monitor.wait()  # el beodo espera la señal, es decir el notify
                    logging.info(f'Beode {self.name} abriendo la heladera {heladera.nombre}')
                    #time.sleep(5)
                    self.tomarUnaCerveza()
                    time.sleep(10) # Beode tomando una birra, por eso lo ponemos a esperar un poco    
                    
        #else: 
        logging.info(f'Beode {self.name} desmayado, no toma mas')
        time.sleep(10)
                    
        

            
heladeras = []

monitorFiesta = threading.Condition()
monitorBeode = threading.Condition()
monitorPinchadura = threading.Condition()

h1 = Heladera(nombre = "h1")
h2 = Heladera(nombre = "h2")
h3 = Heladera(nombre = "h3")
h4 = Heladera(nombre = "h4")
h5 = Heladera(nombre = "h5")

heladeras.append(h1)
heladeras.append(h2)
heladeras.append(h3)
heladeras.append(h4)
heladeras.append(h5)


for i in range(10): # cantidad de proveedores lanzados
    logging.info(f'un proveedor en camino')
    llegadaEn = generarNumeroEntre(2,20) # tiempo de llegada para cada proveedor
    nombre = "proveedor " + str(i)
    # el proveedor entrega tanto producto como se le asigne, si se le asigna 0, ese producto no se entregara
    Proveedor(nombre,generarNumeroEntre(0,15),generarNumeroEntre(0,15),monitorFiesta,heladeras,llegadaEn).start()
    logging.info(f'tiempo de llegada: {llegadaEn} seg')
    timmer(2,4)

# los Beodes si no toman botella o latas, se los instancia en 0
Beodxs("borrachin 1",4,2,monitorBeode,heladeras).start()
Beodxs("borrachin 2",3,8,monitorBeode,heladeras).start()
Beodxs("borrachin 3",0,5,monitorBeode,heladeras).start()

bar(monitorFiesta,monitorBeode,heladeras) # comienza la fiesta en el bar
