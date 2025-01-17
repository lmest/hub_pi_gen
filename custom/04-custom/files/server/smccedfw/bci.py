       
import pytz
import datetime
import struct
from smccedfw.amqp_publish import publish_amqp
from logging_conf import *
import smccedfw.req_recv as req_recv
from wtd_timer import SensorWtdTimer

class BCI_REQ(object):
    def __init__(self, sensor_id, time, unit):
        self.sensor_id = sensor_id
        self.time = time
        self.unit = unit # (0-> seconds, 1-> minutes, 2-> hours))


class BCI(object):
    def __init__(self):
        self.contador = 0
        self.ano = 0 
        self.mes = 0 
        self.dia = 0 
        self.hora = 0
        self.minutos = 0
        self.segundos = 0
        self.sensorid = ''
        self.hubid = 0
        self.flags = 0
        self.pressure = 0
        self.temp = 0
        self.bat = 0
        
    def set_header(self, new_sensorid, new_hid):
        self.sensorid = new_sensorid
        self.hubid = new_hid
        
        fuso = pytz.timezone('America/Sao_Paulo')
        time = datetime.datetime.now(fuso)
        self.ano = time.year
        self.mes = time.month
        self.dia = time.day
        self.hora = time.hour
        self.minutos = time.minute
        self.segundos = time.second
        
    def set_sensor_data(self, pressure, temp, bat):
        self.pressure = pressure
        self.temp     = temp
        self.bat      = bat
        
    def send_data_server(self, pid_str, pressure, temp, bat):
        self.set_header(pid_str, req_recv.hub_id)
        self.set_sensor_data(pressure, temp, bat)
        
        publish_amqp(self)
        logging.info("BCI Sent!")
        SensorWtdTimer().restart_wtd_timer_full_msg()     
        
