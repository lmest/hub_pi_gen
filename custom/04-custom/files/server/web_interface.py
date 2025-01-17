import multitimer
from radio_tx import RadioTx 
from logging_conf import *
import dashboard.send_log as dashboard
from read_config_ini import ConfigIni

web_rssi = 0
web_q_counter = 0
web_num_beacons = 0

def update_web_rssi(rssi):
    global web_rssi
    web_rssi = rssi
    dashboard.PubLog().send_rssi(rssi)

def update_web_q_counter():
    global web_q_counter
    web_q_counter = web_q_counter + 1
    if web_q_counter > 1000:
        web_q_counter = 1    

def get_web_q_counter():
    global web_q_counter
    return web_q_counter
    
def update_num_beacons(num_beacons):
    global web_num_beacons
    web_num_beacons = num_beacons       
            
def update_server():
    try:
        web_ip_lte = ConfigIni().get_ipconfig_hub_ip()
        
        logging.debug("| ----UPDATING WEB SERVER---- |")
        logging.debug("IP LTE: {} | RSSI: {} | AMQP Consume Counter: {} | Num Beacons: {}\n".format(web_ip_lte, web_rssi, web_q_counter, web_num_beacons))
    
        RadioTx().send_update_web_server(web_ip_lte, web_rssi, web_q_counter, web_num_beacons)                
    except Exception as e:
        logging.warning("Web queue error: {}".format(e)) 
    
def start_web_queue():
    timer= multitimer.MultiTimer(interval=60, function=update_server, count=-1, runonstart=False)
    timer.start()
