import configparser
from logging_conf import *

class ConfigIni():
    _instance = None
    _init = None
    
    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance
       
    def __init__(self):
        if self._init is None:
            self._init = True
            self.file_ini = "/home/pi/hub_config.ini"
            self.config_parser = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)  
            self.ini_params = {'radio': {'channel': '', 'pan_id': ''},
                            'server': {'wtd_full_msg': '', 'wtd_server_queue': ''},
                            'ipconfig': {'hub_id': '', 'hub_ip': '', 'net_dev': ''},
                            'webserver': {'user': '', 'psw': '', 'secret_key': ''},
                            'dashboard': {'addr': '', 'port': '', 'action': ''}}
            self.server_addr = ''
            self.sever_port = ''
        
            self.read_config_ini_file()
    
    def _read_config_file_param(self, section, key):
        self.config_parser.read(self.file_ini)
        try:
            v = self.config_parser[section][key].replace("\"","")
            logging.debug("File parameter read -> {} / {} : {}".format(section, key, v))
        except Exception as e:
            logging.warning("Error reading configuration file: {}/{} -> {}".format(section, key, e))
            return None
        else:
            return v
        
    def read_server_addr_port(self):        
        try:
            v = self._read_config_file_param('ipconfig', 'config_server_name')
            
            if v is None:
                return     
                   
            v.replace("\"","")            
            v1 = v.split("/")[2]
                                 
            self.server_addr = v1.split(":")[0]
            self.sever_port = int(v1.split(":")[1])
            
            logging.debug("Server Addr -> ip: {} / port: {} ".format(self.server_addr,self.sever_port))
        except Exception as e:
            logging.warning("Error parsing server addr/port: {}".format(e))

    def read_ipconfig(self):
        self.ini_params['ipconfig']['hub_id'] = self._read_config_file_param('ipconfig', 'hub_id')
        self.ini_params['ipconfig']['hub_ip'] = self._read_config_file_param('ipconfig', 'hub_ip')
        self.ini_params['ipconfig']['net_dev'] = self._read_config_file_param('ipconfig', 'net_dev')

    def read_radio(self):
        self.ini_params['radio']['channel'] = self._read_config_file_param('radio', 'channel')
        self.ini_params['radio']['pan_id'] = self._read_config_file_param('radio', 'pan_id') 
        
    def read_interface(self):
        try:
            net_dev = self._read_config_file_param('ipconfig', 'net_dev')      
            self.ini_params['ipconfig']['net_dev'] = net_dev.replace("\"","")
           
            logging.debug("Network interface-> {} : {}".format("net_dev", self.ini_params['ipconfig']['net_dev']))
        except Exception as e:
            logging.warning("Error parsing network interface: {}".format(e))
    
    def read_webserver(self):
        self.ini_params['webserver']['user'] = self._read_config_file_param('webserver', 'user')
        self.ini_params['webserver']['psw'] = self._read_config_file_param('webserver', 'psw')
        self.ini_params['webserver']['secret_key'] = self._read_config_file_param('webserver', 'secret_key')
    
    def read_dashboard(self):
        self.ini_params['dashboard']['address'] = self._read_config_file_param('dashboard', 'address')
        self.ini_params['dashboard']['port'] = self._read_config_file_param('dashboard', 'port')
        self.ini_params['dashboard']['action'] = self._read_config_file_param('dashboard', 'action')
        
    def read_server(self):
        self.ini_params['server']['wtd_full_msg'] = self._read_config_file_param('server', 'wtd_full_msg')
        self.ini_params['server']['wtd_server_queue'] = self._read_config_file_param('server', 'wtd_server_queue')
    
    def save_new_channel_pan_id(self, channel, pan_id):
        self.config_parser['radio']['channel'] = channel
        self.config_parser['radio']['pan_id'] = pan_id
        with open(self.file_ini, 'w') as configfile:
            self.config_parser.write(configfile)      
                 
    def save_new_ipconfig(self, config_server_name, backend_server_name, backend_server_ip, api_token_name, hub_id):
        self.config_parser['ipconfig']['config_server_name'] = config_server_name
        self.config_parser['ipconfig']['backend_server_name'] = backend_server_name
        self.config_parser['ipconfig']['backend_server_ip'] = backend_server_ip
        self.config_parser['ipconfig']['api_token_name'] = api_token_name
        self.config_parser['ipconfig']['hub_id'] = hub_id
        with open(self.file_ini, 'w') as configfile:
            self.config_parser.write(configfile)        

    def get_dashboard_params(self):
        #return self.ini_params['dashboard']['address'], self.ini_params['dashboard']['port'], self.ini_params['dashboard']['action']
        return 'address', 'port', 'action'
    
    def get_ipconfig_net_dev(self):
        return self.ini_params['ipconfig']['net_dev']
    
    def get_ipconfig_addr(self):
        return self.server_addr
    
    def get_ipconfig_port(self):
        return self.sever_port
    
    def get_ipconfig_hub_id(self):
        return self.ini_params['ipconfig']['hub_id']
    
    def get_ipconfig_hub_ip(self):
        return self.ini_params['ipconfig']['hub_ip']
    
    def get_server_wtd_full_msg(self):
        return self.ini_params['server']['wtd_full_msg']   
    
    def get_server_wtd_server_queue(self):
        return self.ini_params['server']['wtd_server_queue']   
                        
    def read_config_ini_file(self):
        self.read_server_addr_port()
        self.read_interface()
        self.read_ipconfig()
        self.read_radio()
        self.read_webserver()
        #self.read_dashboard()
        self.read_server()