from json_tricks import loads, dumps
from smccedfw.amqp_publish import WriteAMQP, ServerReq, SensorPanIdConfig
import struct

FILA_ESCRITA = dict()
FILA_LEITURA = dict()
filas = dict()

      
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


pid_s2_vet = [49, 0, 31, 0, 17, 80, 67, 80, 80, 52, 55, 32]
request_sensor2 = struct.pack("<12B", *pid_s2_vet)
pid_s2_str = "4903101780678080525532"

def tratar_escrita_fila(mensagem):
    exchange = "EXCHANGE.{}.ESCRITA".format("SMCCEDFW")
    queue = "QUEUE.{}.ESCRITA".format("SMCCEDFW")
    routing_key = "ROUTING_KEY.{}.ESCRITA".format("SMCCEDFW")
    endereco = "127.0.0.1"

    if (endereco in FILA_ESCRITA.keys()):
        filaEscrita = FILA_ESCRITA[endereco]
    else:
        filaEscrita = WriteAMQP(exchange,
                                  queue,
                                  routing_key,
                                  endereco,
                                  5672,
                                  'smccedfw.petro',
                                  'UFE59BBAfQxPSqYvsYM755j74RzKuNjeGSKn3nGasyaibePe')
        FILA_ESCRITA[endereco] = filaEscrita

    filaEscrita.publish_simple(mensagem)


def send_msg():
    requisicao = ServerReq()
    requisicao.sensorid = str(request_sensor2)
    requisicao.hub_ssid = 123
    tratar_escrita_fila(dumps(requisicao))
    
def send_panid_config_msg(channel, panid):
    requisicao = SensorPanIdConfig()
    requisicao.channel = channel
    requisicao.panid = panid
    tratar_escrita_fila(dumps(requisicao))


if __name__ == '__main__':

    while True:
        try:
            channel = int(input("Channel: "))
            panid = int(input("Panid: "))
            
            if 20 < channel < 10 == False:
                print("Invalid channel\n")                
            elif  1 < panid < 100 == False:
                print("Invalid panid\n")    
            else:
                send_panid_config_msg(channel, panid)
                print("Message sent\n")
                        
        except ValueError:
            print("Invalid input")
            continue

