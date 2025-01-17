from json_tricks import loads, dumps
from smccedfw.amqp_consume import ReadQueue
import threading
import datetime

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
    print('Requisicao: {}'.format(requisicao))


def tratar_leitura_fila(endereco):
    exchange = "EXCHANGE.{}.ESCRITA".format("SMCCEDFW")
    queue = "QUEUE.{}.ESCRITA".format("SMCCEDFW")
    routing_key = "ROUTING_KEY.{}.ESCRITA".format("SMCCEDFW")

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
