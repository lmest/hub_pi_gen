import pika
import json_tricks
from retry import retry

class ReadQueue(object):

    conn_rabbit = None
    channel     = None

    def __init__(self, exchange, queue, routing_key, host, port, user,pwd, fn_db):
        self.exchange    = exchange
        self.queue       = queue
        self.routing_key = routing_key
        self.host        = host
        self.port        = port
        self.pwd         = pwd
        self.user        = user
        self.fn_db       = fn_db

    def read(self, ch, method, properties, body):
        try:
            signal = json_tricks.loads(body.decode('latin1'))
            self.fn_db(signal)
        except Exception as e:
            print("Json loads error: {}".format(e))
        
    def connect(self):
        credentials = pika.PlainCredentials(self.user, self.pwd)
        param_conn =  pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials)
        self.conn_rabbit = pika.BlockingConnection(param_conn)
        self.channel = self.conn_rabbit.channel()

    def declare(self):
        self.channel.exchange_declare(exchange=self.exchange)
        self.channel.queue_declare(queue=self.queue, durable=True)

    def bind(self):
        self.channel.queue_bind(exchange=self.exchange, queue=self.queue, routing_key=self.routing_key)

    @retry(delay=5)
    def consume(self):         
        self.log_consume()
        self.connect()
        self.declare()
        self.bind()
        self.channel.basic_consume(queue=self.queue,
                                auto_ack=True,on_message_callback=self.read)
        self.channel.start_consuming()          
    
    def log_consume(self):
        print("{} - Action: Consume ".format(self.queue))
