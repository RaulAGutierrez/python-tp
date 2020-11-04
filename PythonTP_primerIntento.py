# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 00:04:13 2020

@author: Raul A. Gutierrez - Programacion Concurrente
"""

import threading
import time
import logging

logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(threadName)s] - %(message)s', datefmt='%H:%M:%S', level=logging.INFO)


cantidadMaxBotellas = 10
cantidadMaxLatas = 15

class Heladera:
    global cantidadMaxBotellas, cantidadMaxLatas
    
    def __init__(self,nombre,botellas = 0,latas = 0,estaEnchufada = False):
        self.nombre = nombre
        self.botellas = botellas
        self.latas = latas
        self.estaEnchufada = estaEnchufada
        
    def agregarBotella(self):
        self.botellas += 1
        time.sleep(4)
        logging.info(f'botella ingresada, falta {cantidadMaxBotellas - self.botellas}')
    
    def agregarLata(self):
        self.latas += 1
        time.sleep(4)
        logging.info(f'lata ingresada, faltan {cantidadMaxLatas - self.latas}')
    
        
    def estaLlena(self):
        return self.botellas == cantidadMaxBotellas and self.latas == cantidadMaxLatas
    
    def enchufar(self):
        self.estaEnchufada = True          
      
   
class Proveedor(threading.Thread):
    global cantidadMaxBotellas, cantidadMaxLatas
    def __init__(self,nombre,proveeBotellas,proveeLatas,monitorOSemaforo,listaHeladeras):
        super().__init__()
        self.nombre = nombre
        self.proveeBotellas = proveeBotellas
        self.proveeLatas = proveeLatas
        self.monitorOSemaforo = monitorOSemaforo
        self.listaHeladeras = listaHeladeras
        
    def entregaBotella(self):
        self.proveeBotellas -= 1
        time.sleep(4)
        logging.info(f'botella entregada, quedan {self.proveeBotellas}')
        
    def entregaLata(self):
        self.proveeLatas -= 1
        time.sleep(4)
        logging.info(f'lata entregada, quedan {self.proveeLatas}')
        
        
    def entregaCompleta(self):
        return self.proveeBotellas == 0 and self.proveeLatas == 0
    
    def entregarBotellas(self,heladera):
        while not (heladera.botellas < cantidadMaxBotellas or self.proveeBotellas > 0):
            self.entregaBotella()
            heladera.agregarBotella()
            logging.info(f'agregando una botella')
            time.sleep(4)
            
    def entregarLatas(self,heladera):
        while not (heladera.latas < cantidadMaxLatas or self.proveeLatas > 0):
            self.entregaLata()
            heladera.agregarLata()
            logging.info(f'agregando una lata')
            time.sleep(4)
    
    def llenar(self,heladera):
        
            while not heladera.estaEnchufada:
                self.monitorOSemaforo.wait()
            self.entregarBotellas(heladera)
            self.entregarLatas(heladera)
    
    def run(self):
        while (True):
            
            for heladera in self.listaHeladeras: ## recorre la lista de heladeras
                
                ##if not heladera.estaLlena():
                logging.info(f'la heladera {heladera.nombre} no esta llena')
                with self.monitorOSemaforo:
                        ##self.llenar(heladera)
                        while not heladera.estaEnchufada and not heladera.estaLlena():
                            logging.info(f'esperando {heladera.nombre}')
                            self.monitorOSemaforo.wait()
                        self.entregarBotellas(heladera)
                        self.entregarLatas(heladera)
                        logging.info(f'heladera {heladera.nombre} es llena heladera.estaLlena')
                        time.sleep(4)
                
                
                if (self.entregaCompleta):
                    break
            ##if (self.entregaCompleta):
                    ##break

def fiesta(monitor,listaHeladeras):
    global cantidadMaxBotellas, cantidadMaxLatas
    logging.info(f'Comienza la fiesta')
    while (True):
        
        
        logging.info(f'controlemos las heladeras')
        for heladera in listaHeladeras: ## recorre la lista de heladeras
            
            logging.info(f'veremos la heladera {heladera.nombre}')
            time.sleep(4)

            
            with monitor:
                if heladera.estaEnchufada and not heladera.estaLlena():
                    logging.info(f'la heladera {heladera.nombre} no esta llena')
                    monitor.notify()
                    time.sleep(4)
                else:
                    logging.info(f'la heladera {heladera.nombre} esta llena o apagada')
                    time.sleep(4)
            
            """"
            if not heladera.estaEnchufada:
                logging.info(f'la heladera {heladera.nombre} esta apagada')
                time.sleep(4)
                heladera.enchufar()
                logging.info(f'la heladera {heladera.nombre} esta enchufada')
                time.sleep(4)
            """    
            

            
heladeras = []

monitorFiesta = threading.Condition()

h1 = Heladera(nombre = "h1")
h1.enchufar()
h2 = Heladera(nombre = "h2")
h2.enchufar()

heladeras.append(h1)
heladeras.append(h2)

proveedor1 = Proveedor("Proveedor1",7,5,monitorFiesta,heladeras)
proveedor1.start()

fiesta(monitorFiesta,heladeras)
