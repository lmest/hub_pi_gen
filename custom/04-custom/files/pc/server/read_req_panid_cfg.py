import json
from smccedfw.amqp_consume import ReadQueue
import threading

FILA_LEITURA = dict()
filas = dict()
endereco = "127.0.0.1"


def iniciar(exchange, queue, routing_key, host, port, user, pwd, fn_db):
    def iniciar_fila_consumo(exchange, queue, routing_key, host, port, user, pwd, fn_db):
        filaLeitura = ReadQueue(exchange,
                                  queue,
                                  routing_key,
                                  host,
                                  port,
                                  user,
                                  pwd,
                                  fn_db)
        filaLeitura.consume()

    thread = threading.Thread(target=iniciar_fila_consumo,
                              args=(exchange, queue, routing_key, host, port, user, pwd, fn_db))
    thread.start()


def teste_leitura(requisicao):
    try:
        req_json = json.loads(requisicao)
        print('Req: {}'.format(req_json))
        
        if req_json["__instance_type__"][1] == "SensorPanIdConfig":
            print("New SensorPanIdConfig")
            channel = int(req_json["attributes"]["channel"])
            panid = int(req_json["attributes"]["panid"])
            print("Channel: {}".format(channel))
            print("Panid: {}".format(panid))
    except Exception as e:
        print("Error: {}".format(e))


def tratar_leitura_fila(endereco):
    exchange = "EXCHANGE.{}.LEITURA".format("SMCCEDFW")
    queue = "QUEUE.{}.LEITURA".format("SMCCEDFW")
    routing_key = "ROUTING_KEY.{}.LEITURA".format("SMCCEDFW")

    if (endereco in FILA_LEITURA.keys()):
        print('*')
    else:
        iniciar(exchange,
                queue,
                routing_key,
                endereco,
                5672,
                'smccedfw.petro',
                'UFE59BBAfQxPSqYvsYM755j74RzKuNjeGSKn3nGasyaibePe',
                teste_leitura)
        FILA_LEITURA[endereco] = '******FILA CRIADA*********'


def main():
    tratar_leitura_fila(endereco)


if __name__ == "__main__":
    main()
