import json_tricks
from smccedfw.amqp_consume import ReadQueue
import threading
from threading import *

FILA_LEITURA = dict()
filas = dict()
endereco = "127.0.0.1"
lista_pedidos = dict()
hub_id = 0
LIST_ERROR = -1
LIST_OK = 0
obj_sem = Semaphore(1)
q_consume_counter = 0

WAVEFORM_REQ = 0
GLOBALS_REQ = 1
NO_REQ = 2

def check_list(sensor_id):
    obj_sem.acquire()
    if sensor_id in lista_pedidos:
        if lista_pedidos[sensor_id] != 0:
            check_return = WAVEFORM_REQ
        else:
            check_return = GLOBALS_REQ
    else:
        check_return = NO_REQ
    obj_sem.release()
    return check_return


def remove_list_item(sensor_id):
    obj_sem.acquire()
    if sensor_id in lista_pedidos:
        del lista_pedidos[sensor_id]
        remove_status = LIST_OK        
    else:
        remove_status = LIST_ERROR
    obj_sem.release()
    return remove_status


def add_list_item(sensor_id, cont):
    obj_sem.acquire()
    if sensor_id not in lista_pedidos:
        lista_pedidos[sensor_id] = cont
    obj_sem.release()


def get_list_cnt(sensor_id):
    obj_sem.acquire()
    if sensor_id in lista_pedidos:
        list_cnt = lista_pedidos[sensor_id]
    else:
        list_cnt = LIST_ERROR
    obj_sem.release()
    return list_cnt


def escrever_pedido(requisicao):
    contador = int(requisicao.contador)
    add_list_item(requisicao.sensorid, contador)
    global hub_id
    hub_id = requisicao.hub.ssid

    print('Server Requests{}'.format(lista_pedidos))


def realizar_ciclo_aquisicoes(requisicao):
    escrever_pedido(requisicao)


def log_consumo():
    print("{} - Acao: Thread criada ".format("CICLO AQUISICAO"))


def iniciar(exchange, queue, routing_key, host, port, user,pwd, fn_db):

    def iniciar_fila_consumo(exchange, queue, routing_key, host, port, user,pwd, fn_db):    
        filaLeitura = ReadQueue(exchange,
             queue,
             routing_key,
             host,
             port,
             user,
             pwd,
             fn_db)
        filaLeitura.consume()

    thread = threading.Thread(target=iniciar_fila_consumo, args=(exchange, queue, routing_key, host, port, user,pwd, fn_db))
    thread.start()


def tratar_leitura_fila(endereco):
     exchange    = "EXCHANGE.{}.ESCRITA".format("SMCCEDFW")
     queue       = "QUEUE.{}.ESCRITA".format("SMCCEDFW")
     routing_key = "ROUTING_KEY.{}.ESCRITA".format("SMCCEDFW")
     if( endereco in FILA_LEITURA.keys()):
                   print('*')
     else:
                   iniciar(exchange,
                           queue,
                           routing_key,
                           endereco,
                           5672,
                           'smccedfw.petro',
                           'UFE59BBAfQxPSqYvsYM755j74RzKuNjeGSKn3nGasyaibePe',
                           realizar_ciclo_aquisicoes)
                   FILA_LEITURA[endereco] = '******FILA CRIADA*********'


def main():
    tratar_leitura_fila(endereco)
    
class Requisicao(object):
    def __init__(self, contador, 
                       ano, 
                       mes, 
                       dia, 
                       hora, 
                       minutos, 
                       segundos, 
                       sensorid, 
                       codigo_ponto,
                       flags,
                       audio_rate,
                       audio_size,
                       vibro_rate,
                       vibro_size,
                       hub):
        self.contador             = contador
        self.ano                  = ano
        self.mes                  = mes
        self.dia                  = dia
        self.hora                 = hora
        self.minutos              = minutos
        self.segundos             = segundos
        self.sensorid             = sensorid
        self.codigo_ponto         = codigo_ponto
        self.hub                  = hub
        self.flags                = flags
        self.audio_rate           = audio_rate
        self.audio_size           = audio_size
        self.vibro_rate           = vibro_rate
        self.vibro_size           = vibro_size