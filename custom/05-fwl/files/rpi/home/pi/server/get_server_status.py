import socket
from radio_tx import RadioTx 
import multitimer
import os_mng
from serial import *
from logging_conf import *
import dashboard.send_log as dashboard
import smccedfw.req_recv as req_recv
from read_config_ini import ConfigIni

class Get_ServerStatus():       
    def __init__(self):
        self.file_ini = "/home/pi/hub_config.ini"
        self.server_ip = ""
        self.server_port = ""
        self.reply_status = False
        self.radio_process_restarted = False
        self.config_ini = ConfigIni()
        
    def set_reply_status(self):
        self.reply_status = True    
        
    def check_reply_status(self):
        if self.reply_status == False:
            if self.radio_process_restarted == False:
                logging.warning("Radio process did not respond request - Restarting it!\n")
                os_mng.restart_radio_script()
                self.radio_process_restarted = True
            else:
                logging.warning("Radio process did not respond request - Rebooting system!\n")
                os_mng.reboot_system()
        self.reply_status = False
                    
    def get_server_addr_port(self):
        try:
            self.server_ip = self.config_ini.get_ipconfig_addr()
            self.server_port = self.config_ini.get_ipconfig_port()
            logging.info("Server Addr -> ip: {} / port: {} ".format(self.server_ip,self.server_port))
        except Exception as e:
            logging.warning("Error reading configuration file: {}".format(e))
            
    def get_hub_id(self):
        last_id = req_recv.get_hub_id()
        
        if last_id != 0:
            return
        
        try:
            id  = self.config_ini.get_ipconfig_hub_id().replace("\"","")
            req_recv.set_hub_id(f"HUB-{id}")
            dashboard.PubLog().set_hubid(id)
        except Exception as e:
            logging.warning("Error reading configuration file: {}".format(e))
        
    def check_server_status(self,timeout=3):
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.server_ip, self.server_port))
            return 1
        except socket.error as ex:
            logging.warning("Server connection fail: {}".format(ex))
            return 0    
        
    def get_server_status(self):
        try:
            logging.debug("| ----Checking Server Status---- |")
            self.get_server_addr_port()
            self.get_hub_id()
            status = self.check_server_status()
            logging.info("Server Connection Status: {} \n".format(status))
            RadioTx().send_server_status(status)
            
            check_reply = multitimer.MultiTimer(interval=10, function=self.check_reply_status, count=1, runonstart=False)
            check_reply.start()
        
        except Exception as e:
            logging.warning("Server status error: {}".format(e)) 
    
    def start(self):
        self.timer= multitimer.MultiTimer(interval=55, function=self.get_server_status, count=-1, runonstart=True)
        self.timer.start()
