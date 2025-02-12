'''
Used for full wireless sensor for backward 
compatibility with backend server

'''
import numpy as np
import pytz
import datetime
import struct
from logging_conf import *

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


class ConfigHub(object):
    def __init__(self,descricao_hub, endereco, ssid):
        self.descricao_hub = descricao_hub
        self.endereco      = endereco
        self.ssid          = ssid


class ServerReq(object):
    def __init__(self):
        self.sensorid = 0
        self.hub_ssid = 0
        

class Sinal(object):
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
        self.audio_sample_rate = 0
        self.audio_sample_size = 0
        self.vibration_sample_rate = 0
        self.vibration_sample_size = 0
        self.vib_rms1 = 0
        self.vib_max1 = 0
        self.vib_rms2 = 0
        self.vib_max2 = 0
        self.temperatura = 0
        self.battery = 0
        self.waveform_audio = 0
        self.waveform_vibracao1 = 0
        self.waveform_vibracao2 = 0
        self.num_beacons = 0
        self.rssi = 0
        self.q_consume = 0        
    
    def set_header(self, new_cont, new_sensorid, new_hid, new_flags, new_aud_sr, new_aud_ss, new_vib_sr, new_vib_ss):
        self.contador = new_cont
        self.sensorid = new_sensorid.decode('latin1')
        self.hubid = new_hid
        self.flags = new_flags
        self.audio_sample_rate = new_aud_sr * 1000
        self.audio_sample_size = new_aud_ss 
        self.vibration_sample_rate = new_vib_sr * 1000
        self.vibration_sample_size = new_vib_ss
        
        fuso = pytz.timezone('America/Sao_Paulo')
        time = datetime.datetime.now(fuso)
        self.ano = time.year
        self.mes = time.month
        self.dia = time.day
        self.hora = time.hour
        self.minutos = time.minute
        self.segundos = time.second
        
        logging.info("Header set -> Sensor: {} | Hub: {}".format(self.sensorid, self.hubid))
        
    def set_sensor_data(self, globais, rssi, q_consume, buff_audio, buff_vib1, buff_vib2, aud_size, vib_size):
        self.vib_rms1 = globais[0]
        self.vib_max1 = globais[1]
        self.vib_rms2 = globais[2]
        self.vib_max2 = globais[3]
        self.temperatura = globais[4]
        self.battery = globais[5]
        self.num_beacons = globais[6]
        self.rssi = rssi
        self.q_consume = q_consume
        
        waveform_audio = struct.unpack('<{}s'.format(aud_size), buff_audio)[0]
        self.waveform_audio = np.frombuffer(waveform_audio, dtype=np.uint16, offset=0)/10000
        
        waveform_vibracao1 = struct.unpack('<{}s'.format(vib_size), buff_vib1)[0]
        self.waveform_vibracao1 = np.frombuffer(waveform_vibracao1, dtype=np.uint16, offset=0)/10000
        
        waveform_vibracao2 = struct.unpack('<{}s'.format(vib_size), buff_vib2)[0]
        self.waveform_vibracao2 = np.frombuffer(waveform_vibracao2, dtype=np.uint16, offset=0)/10000

