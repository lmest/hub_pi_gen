import json
from smccedfw.amqp_consume import ReadQueue
from wtd_timer import SensorWtdTimer
import threading
from threading import *
from logging_conf import *
import web_interface 
from smccedfw.pan_cfg import PanCfgReq
import traceback
import dashboard.send_log as dashboard

FILA_LEITURA = dict()
filas = dict()
endereco = "127.0.0.1"
lista_pedidos = dict()
hub_id = 0
LIST_ERROR = -1
LIST_OK = 0
obj_sem = Semaphore(1)
q_consume_counter = 0
pan_cfg = PanCfgReq()

WAVEFORM_REQ = 0
GLOBALS_REQ = 1
NO_REQ = 2

def get_hub_id():
    return hub_id

def set_hub_id(hub):
    global hub_id
    hub_id = hub

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
    ret = False
    if (sensor_id not in lista_pedidos) or cont != 0:
        lista_pedidos[sensor_id] = cont
        ret = True
        logging.info("Request added to list -> Sensor:{} / Count:{}".format(sensor_id, cont))
    else:
        logging.info("Request ignored in list -> Sensor:{} / Count:{}".format(sensor_id, cont))
    obj_sem.release()
    return ret


def get_list_cnt(sensor_id):
    obj_sem.acquire()
    if sensor_id in lista_pedidos:
        list_cnt = lista_pedidos[sensor_id]
    else:
        list_cnt = LIST_ERROR
    obj_sem.release()
    return list_cnt


def escrever_pedido(requisicao):
    try:
        req_usage_status = False
        req_json = json.loads(requisicao)
        #logging.info('Req: {}'.format(req_json))
        
        if type(req_json) is not dict:
            req_json = json.loads(req_json)            
        
        if req_json["__instance_type__"][1] == "SensorPanIdConfig":
            channel = int(req_json["attributes"]["channel"])
            panid = int(req_json["attributes"]["panid"])
            sensorid = req_json["attributes"]["sensorid"]
            timeout = int(req_json["attributes"]["minutes"])
            pan_cfg.add_list_item(sensorid, channel, panid, timeout)

            logging.info('Panid Config Request{}'.format(pan_cfg.get_req_list()))
            
        elif req_json["__instance_type__"][1] == "Requisicao":
            contador = int(req_json["attributes"]["contador"]) 
            sensorid = req_json["attributes"]["sensorid"]
            req_usage_status = add_list_item(sensorid, contador)
            
            global hub_id
            hub_id = req_json["attributes"]['hub']["attributes"]["ssid"]
            web_interface.update_web_q_counter()
            
            dashboard.PubLog().set_ssid(hub_id)
            
            logging.info('Server Requests{}'.format(lista_pedidos))
            SensorWtdTimer().restart_wtd_timer_server_queue()
            dashboard.PubLog().send_request_received_from_server(req_json, req_usage_status)
            
    except Exception as e:    
        logging.warning("Error: {}".format(e))
        logging.warning("Error: {}".format(traceback.format_exc()))


def realizar_ciclo_aquisicoes(requisicao):
    escrever_pedido(requisicao)


def log_consumo():
    logging.debug("{} - Acao: Thread criada ".format("CICLO AQUISICAO"))


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