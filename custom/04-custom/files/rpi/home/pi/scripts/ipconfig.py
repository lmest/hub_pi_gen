import configparser
import time
import pytz
import datetime
import requests
import logging
import sys
import json
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    datefmt='%d-%b-%y %H:%M:%S'
)

class IpConfig:
    def __init__(self):
        self.hub_config_file = "/home/pi/hub_config.ini" #"hub_config.ini"
        self.config_parser = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
        self.file_data = {'net_dev': self.get_config_file_param("net_dev"),
                          'hub_id': self.get_config_file_param("hub_id"),
                          'api_token_name': self.get_config_file_param("api_token_name"),
                          'config_server_name': self.get_config_file_param("config_server_name"),
                          'backend_server_name': self.get_config_file_param("backend_server_name"),
                          'backend_server_ip': self.get_config_file_param("backend_server_ip"),
                          'hub_ip': self.get_config_file_param("hub_ip"),
                          'channel': self.get_config_file_param("channel", "radio"),
                          'pan_id': self.get_config_file_param("pan_id", "radio")}   
        self.network_data = {'id': self.get_rasp_id(),'tag': f"HUB-{self.file_data['hub_id']}",#HUB-IMEI
                             'timestamp' : 0, 'ip' : " ",
                             'channel': self.file_data['channel'], 'pan_id': self.file_data['pan_id']}
        self.http_resp = 0
        self.sleep_next_try_sec = 10
        self.sleep_next_update_sec = 120
        self.receive_json = True
           
    def get_config_file_param(self, key, section='ipconfig'):
        self.config_parser.read(self.hub_config_file)
        try:
            v = self.config_parser[section][key].replace("\"","")
            logging.info("File parameter read -> {} : {}".format(key, v))
        except Exception as e:
            logging.warning("Error reading configuration file: {}".format(e))
        else:
            return v
    
    def set_config_file_param(self, key, value):
        self.config_parser.read(self.hub_config_file)
        self.config_parser.set("ipconfig", key, value)                         
        cfgfile = open(self.hub_config_file,'w')
        self.config_parser.write(cfgfile)  
        cfgfile.close()        
    
    def update_file_data_var(self, key, value):    
        logging.info("Updating file data -> {} : {}".format(key, value))
        self.file_data.update({key: value})
        self.set_config_file_param(key, str("\"") + value + str("\""))                 

    def get_rasp_id(self):
        return self.file_data['hub_id']
    
    def get_rasp_ip(self):
        try:
            ip = os.popen(f'ip addr show {self.file_data["net_dev"]} | grep "\<inet\>"').read().strip().split()[1]
            if ip.find('/') > 0:
                ip = ip.split('/')[0]
        except:
            logging.info(f'Missing interface {self.file_data["net_dev"]} using failback IP {self.file_data["hub_ip"]}')
            ip = self.file_data["hub_ip"]
        return ip
    
    def set_network_data_ts(self):
        timezone = pytz.timezone('America/Sao_Paulo')
        self.network_data.update({'timestamp': datetime.datetime.now(timezone).timestamp()})
     
    def get_token(self):
        url_base = self.file_data['api_token_name'] # "http://sesausmcced01.petrobras.com.br:5001/api/token/"
        data = {"username" : "configura.hub", "password" : "97ecd2a1d5b6f77fdc2b29fc46758bea"}
        try:
            logging.info("Get token url base -> {}".format(url_base))
            logging.info("Get token data sent -> {}".format(data))
            r = requests.post(url_base,data=data)
            logging.info(f"get_token() {r}") 
            status_code = r.status_code
        except:
            status_code = 0
        if status_code == 200:
            resposta = r.json()
            if "access" in resposta.keys():
                logging.info(f"response {resposta}")
                return resposta['access']
            else:
                logging.info(f"erro")
                return None
        else:
            logging.info("Unable to get token")
            return None                           
        
    def post_network_data(self, dst, data):
        try:
            logging.info("Post to server: {} with data: {}".format(dst, data)) 
            json_data = json.dumps(data) 
            token = self.get_token()            
            if token:  
                header = {'Authorization' : 'Bearer ' + token}
                r_post = requests.post(dst, json = json_data, headers=header)
                status_code = r_post.status_code   
                logging.info(f"post_network_data() {r_post}")    
                if status_code == 200:                
                    return True                 
        except Exception as e:
            logging.warning("Post Exception: {}".format(e))  
            
        return False
        
    def send_new_data(self):
        self.set_network_data_ts()
       
        if self.post_network_data(self.file_data['config_server_name'], self.network_data):
            logging.info(f'Config server ok')
            return True      
        
        return False
    
    def check_ip_lte_change(self):
        if self.get_rasp_ip() != self.file_data["hub_ip"]:
            self.update_file_data_var('hub_ip', self.get_rasp_ip())
        
        self.network_data.update({'ip': self.get_rasp_ip()})
        
        if self.send_new_data():
            logging.info("Send data status: Success")
            logging.info("Next update in {} sec\n".format(self.sleep_next_update_sec))
            time.sleep(self.sleep_next_update_sec) 
        else:
            logging.warning("Send data status: Error") 
            logging.warning("Next try in {} sec\n".format(self.sleep_next_try_sec))
            time.sleep(self.sleep_next_try_sec)              
    
    def run(self):
        while True:
            self.check_ip_lte_change()
            #time.sleep(20)
                

if __name__ == '__main__':
    logging.info("Starting automatic IP configurator\n")
    ipconfig = IpConfig()
    try:
        ipconfig.run()
    except Exception as e:
            logging.warning("Exception: {}".format(e))    
