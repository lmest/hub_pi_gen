import requests
import datetime
import pytz
from json_tricks import dumps
from subprocess import check_output
from dashboard.mensagem import Mensagem
from logging_conf import *
from read_config_ini import ConfigIni

class SendLog(object):
    _instance = None
    _init = None
    
    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._init is None:
            self._init = True
            self.config = ConfigIni()
            
            self.addr , self.port, self.action = self.config.get_dashboard_params()
            #logging.info(f'Dashboard Info -> Addr: {self.addr} | Port: {self.port} | Action: {self.action}')            
            
    def get_token(self):
        url_base = self.addr + ':' + self.port + '/api/token/'
        logging.debug("Getting token from: " + url_base)
        data = {"username": "smccedfw.aquisicao", "password": "tempestade"}
        r = requests.post(url_base, data=data)
        if r.status_code == 200:
           resposta = r.json()
           if "access" in resposta.keys():
               return resposta['access']
           else:
               return None
        else:
            logging.error("Failed to get token. Status code: " + str(r.status_code))
        return None
    
    def send(self, msg):
        token = self.get_token()
        if( token is not None):
            url                = self.addr + ':' + self.port + '/' + self.action
            header             = {'Authorization': 'Bearer ' + token}
            r                  = requests.post(url, data=dumps(msg), headers=header)
        return r.status_code
    
class PubLog(object):
    _instance = None
    _init = None
    
    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance
       
    def __init__(self):
        if self._init is None:
            self._init = True
            self.ssid = 0
            self.dashboard = SendLog()
            self.hubid = 0
        
    def set_ssid(self, ssid):
        self.ssid = ssid        
    
    def set_hubid(self, hubid):
        self.hubid = hubid
        
    def _send(self, vars, context, type): 
        '''
        try:      
            parametros = {"contexto": context,
                        "tipo"    : type,
                        "hubid"   : self.hubid,
                        "mensagen": vars}
            
            msg = Mensagem(parametros, self.ssid, type)
            
            x = self.dashboard.send(msg)        
            logging.info("Log {} Sent. Message: {}. Status: {} ".format(type, str(parametros), str(x)))    
        except Exception as e:
            logging.error("Error publishing log: {}".format(e))
        '''
        pass
                      
    def send_beacon_fwl(self, pid, vib_x_rms, vib_x_max, vib_z_rms, vib_z_max, temp, bat, sensor_zid, num_beacons):
        vars = {"sensor_id": pid,
                "vib_x_rms": vib_x_rms,
                "vib_x_max": vib_x_max,
                "vib_z_rms": vib_z_rms,
                "vib_z_max": vib_z_max,
                "temp"     : temp,
                "bat"      : bat,
                "sensor_zid": sensor_zid,
                "num_beacons": num_beacons}

        self._send(vars, "comunicacao_sensor", "BEACON_FWL")

    def send_request_ack(self, pid, ack):
        variaveis = {"sensor_id": pid,
                     "ack"   : ack}        
        self._send(variaveis, "comunicacao_sensor", "REQ_ACK")
        
    def send_num_retries(self, pid, num_retries):
        variaveis = {"sensor_id": pid,
                     "ack"   : num_retries}        
        self._send(variaveis, "comunicacao_sensor", "NUM_RETRIES")

    def send_waveform_completed(self, pid):
        variaveis = {"sensor_id": pid}        
        self._send(variaveis, "comunicacao_sensor", "WAVEFORM_COMPLETED")
        
    def send_request_received_from_server(self, request, status):
        variaveis = {"request" : request,
                     "status"  : status}        
        self._send(variaveis, "comunicacao_servidor", "REQ_RECEIVED")      
        
    def send_rssi(self, rssi):
        variaveis = {"rssi" : rssi}        
        self._send(variaveis, "comunicacao_servidor", "RSSI")    
           
    def send_script_start_time(self):
        timezone_nw = pytz.timezone('America/Sao_Paulo')
        time = datetime.datetime.now(timezone_nw)
        time_fmt  = "{0:%d/%b/%Y %H:%M:%S}".format(time)
        
        variaveis = {"time" : time_fmt}        
        self._send(variaveis, "comunicacao_servidor", "SCRIPT_START_TIME")
       
    def send_cpu_temp(self):
        temp_str = str(check_output(["vcgencmd", "measure_temp"]).decode('utf-8'))
        start = temp_str.index( "=" ) + len( "=" )
        end = temp_str.index( "\n", start )
        temp = temp_str[start:end]
        
        variaveis = {"temp" : temp}        
        self._send(variaveis, "status_hub", "CPU_TEMP")
    
    def send_ssh_access(self):
        ssh_access = str(check_output(["sudo", "systemctl", "status", "ssh"]).decode('utf-8'))
                
        variaveis = {"access" : ssh_access}        
        self._send(variaveis, "status_hub", "SSH_ACCESS")       
    
    def send_zigbee_queue(self, queue):                
        variaveis = {"queue" : queue}        
        self._send(variaveis, "status_hub", "ZIGBEE_QUEUE") 
    
    def send_amqp_req(self, new_req_id, new_req_cnt, req_list):                
        variaveis = {"new_req" : {new_req_id : new_req_cnt},
                     "req_list": req_list}        
        self._send(variaveis, "status_hub", "AMQP_REQ") 
        
    def send_startup_hub_info(self):
        self.send_script_start_time()
        self.send_cpu_temp()
        self.send_ssh_access()