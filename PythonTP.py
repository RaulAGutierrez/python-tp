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
semaforoProveedor = threading.Semaphore(1)

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
        #logging.info(f'{self.nombre}-> botella ingresada, faltan {cantidadMaxBotellas - self.botellas}')
        time.sleep(4)
    
    def agregarLata(self):
        self.latas += 1
        #logging.info(f'{self.nombre}-> lata ingresada, faltan {cantidadMaxLatas - self.latas}')
        time.sleep(4)
          
    def estaLlena(self):
        return (self.botellas == cantidadMaxBotellas) and (self.latas == cantidadMaxLatas)
    
    def enchufar(self):
        self.estaEnchufada = True          
      
   
class Proveedor(threading.Thread):
    global cantidadMaxBotellas,cantidadMaxLatas
    def __init__(self,nombre,proveeBotellas,proveeLatas,monitor,listaHeladeras,llegada):
        super().__init__()
        self.nombre = nombre
        self.proveeBotellas = proveeBotellas
        self.proveeLatas = proveeLatas
        self.monitor = monitor
        self.listaHeladeras = listaHeladeras
        self.llegada = llegada
        
    def entregaBotella(self):
        self.proveeBotellas -= 1
        logging.info(f'botella entregada, quedan {self.proveeBotellas}')
        time.sleep(4)
        
    def entregaLata(self):
        self.proveeLatas -= 1
        logging.info(f'lata entregada, quedan {self.proveeLatas}')
        time.sleep(4)
           
    def entregaCompleta(self):
        return (self.proveeBotellas == 0) and (self.proveeLatas == 0)
    
    def entregarBotellas(self,heladera):
        while (heladera.botellas < cantidadMaxBotellas and self.proveeBotellas > 0):
            self.entregaBotella()
            heladera.agregarBotella()
            
    def entregarLatas(self,heladera):
        while (heladera.latas < cantidadMaxLatas and self.proveeLatas > 0):
            self.entregaLata()
            heladera.agregarLata()
    
    def run(self):
        time.sleep(self.llegada) # tiempo de llegada del proveedor

        while (True): 
            
            with self.monitor:  ## Sincroniza para no pizarse con otro proveedor

                for heladera in self.listaHeladeras: ## recorre la lista de heladeras
                    
                    # la condicion por la cual podra agregara productos a la heladera
                    if not heladera.estaLlena() and heladera.estaEnchufada and not self.entregaCompleta():
                    
                        logging.info(f'la heladera {heladera.nombre} esta enchufada')
                        logging.info(f'la heladera {heladera.nombre} no esta llena')
                        self.entregarBotellas(heladera)
                        self.entregarLatas(heladera)
                        
                        while not heladera.estaLlena(): # si la heladera aun no esta llena
                            logging.info(f'{heladera.nombre} no esta llena, para seguir debe estarlo')
           


def bar(monitor,listaHeladeras):
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
            
            # segun si NO esta llena, informamos la cantidad de botellas y latas que tiene
            if not heladera.estaLlena():
                logging.info(f'la heladera {heladera.nombre} no esta llena')
                logging.info(f'{heladera.nombre} tiene {heladera.botellas} botellas')
                logging.info(f'{heladera.nombre} tiene {heladera.latas} latas')
                time.sleep(10)
            else: # si esta llena, informamos la cantidad final de botellas y latas
                logging.info(f'{heladera.nombre} quedo {heladera.botellas} botellas')
                logging.info(f'{heladera.nombre} quedo {heladera.latas} latas')
                logging.info(f'la heladera {heladera.nombre} Llena -> boton de enfriando')
                time.sleep(10)
    

            
heladeras = []

monitorFiesta = threading.Condition()

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
    timmer(5,9)
    llegadaEn = generarNumeroEntre(2,20) # tiempo de llegada para cada proveedor
    Proveedor("Proveedor{i}",generarNumeroEntre(4,9),generarNumeroEntre(3,15),monitorFiesta,heladeras,llegadaEn).start()
    logging.info(f'tiempo de llegada: {llegadaEn} seg')

bar(monitorFiesta,heladeras) # comienza la fiesta en el bar
