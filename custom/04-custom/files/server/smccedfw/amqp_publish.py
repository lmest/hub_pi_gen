import pika
from json_tricks import dumps
import pytz
import datetime
from logging_conf import *

WRITE_QUEUE = dict()

class WriteAMQP(object):

    conn_rabbit     = None
    channel_rabbit  = None

    def __init__(self,exchange, queue, routing_key, host, port, user, pwd):
        self.exchange = exchange
        self.queue    = queue
        self.routing_key = routing_key
        self.host = host
        self.port = port
        self.pwd  = pwd
        self.user = user

    def connect(self):
        credentials = pika.PlainCredentials(self.user, self.pwd)
        params_conn =  pika.ConnectionParameters(host=self.host, port=self.port,  credentials=credentials)
        self.conn_rabbit = pika.BlockingConnection(params_conn)
        self.channel_rabbit = self.conn_rabbit.channel()

    def declare(self):
        self.channel_rabbit.exchange_declare(exchange=self.exchange)
        self.channel_rabbit.queue_declare(queue=self.queue, durable=True)

    def publish(self, sinal):
        self.connect()
        self.declare()
        self.channel_rabbit.basic_publish(exchange=self.exchange,
                                routing_key=self.routing_key,
                                body=dumps(sinal),
                                properties=pika.BasicProperties(content_type='application/json',
                                delivery_mode=2))
        self.conn_rabbit.close()

    def publish_simple(self, mensagem):
        self.connect()
        self.declare()
        self.channel_rabbit.basic_publish(exchange=self.exchange,
                                routing_key=self.routing_key,
                                body=dumps(mensagem),
                                properties=pika.BasicProperties(content_type='application/json',
                                delivery_mode=2))
        self.conn_rabbit.close()

    def log_publish(self):
        timezone_nw = pytz.timezone('America/Sao_Paulo')
        data_hora = datetime.datetime.now(timezone_nw)
        data_fmt  ="{0:%d/%b/%Y %H:%M:%S}".format(data_hora)
        logging.info("| {} - Action Publish ".format(self.queue))

def publish_amqp(mensagem):
        exchange    = "EXCHANGE.{}.LEITURA".format("SMCCEDFW")
        queue       = "QUEUE.{}.LEITURA".format("SMCCEDFW")
        routing_key = "ROUTING_KEY.{}.LEITURA".format("SMCCEDFW")
        addr = "127.0.0.1"

        if( addr in WRITE_QUEUE.keys()):
                    write_queue = WRITE_QUEUE[addr]
        else:
                    write_queue = WriteAMQP(exchange,
                                queue,
                                routing_key,
                                addr,
                                5672,
                                'smccedfw.petro',
                                'UFE59BBAfQxPSqYvsYM755j74RzKuNjeGSKn3nGasyaibePe')
                    WRITE_QUEUE[addr] = write_queue
        write_queue.publish(mensagem)