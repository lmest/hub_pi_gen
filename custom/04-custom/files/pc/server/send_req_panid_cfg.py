from json_tricks import loads, dumps
from smccedfw.amqp_publish import WriteAMQP, ServerReq, SensorPanIdConfig, publish_amqp
  
# sensorid = "3003701780678080525532"

def send_panid_config_msg(channel, panid, sensorid):
    requisicao = SensorPanIdConfig()
    requisicao.channel = channel
    requisicao.panid = panid
    requisicao.sensorid = sensorid
    publish_amqp(dumps(requisicao))

if __name__ == '__main__':

    while True:
        try:
            channel = int(input("Channel: "))
            panid = int(input("Panid: "))
            sensorid = input("Sensor ID: ")
            
            if 20 < channel < 10 == False:
                print("Invalid channel\n")                
            elif  1 < panid < 100 == False:
                print("Invalid panid\n")    
            else:
                send_panid_config_msg(channel, panid, sensorid)
                print("Message sent\n")
                        
        except ValueError:
            print("Invalid input")
            continue

