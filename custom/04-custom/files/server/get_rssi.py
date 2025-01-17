import multitimer
from serial import *
import time
import ipaddress
import os
from logging_conf import *
import web_interface 
from subprocess import check_output
from read_config_ini import ConfigIni

class GetRSSI():
    def __init__(self):
        self.serial = 0
        self.raw_rssi = 0
        self.rssi_hub = 0
        self.net_interface = 'wlan0'
        self.lte_restart_cnt = 0
        self.hub_restart_cnt = 0
        self.lte_status = 0
        self.lte_ip = -1
                
    def connect_serial(self,):
        try:
            self.serial = Serial(port='/dev/ttyUSB2', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1)
        except Exception as e:
            logging.warning("Serial connection warning: {}".format(e))

    def tx_at_command(self, cname):
        try:
            cmd_dic = {"rssi": "AT+CSQ\r", "reset": "AT+CFUN=1,1\r", "status": "AT+CREG?\r", "ip" : "AT+CGPADDR=1\r"}
            cmd=cmd_dic[cname]
            self.serial.write(cmd.encode())
        except Exception as e:
            logging.warning(repr(e))                  
    
    def rx_at_command(self):
        try:
            msg=self.serial.read(64)
        except Exception as e:
            logging.warning(repr(e))

        if not msg:
            logging.warning("No USB response")
        else:
            logging.debug("AT response: {}".format(msg))        

            if b'OK' in msg:
                if b'CSQ' in msg:
                    return self.read_rssi(str(msg))
                elif b'CREG' in msg:
                    return self.read_status(str(msg))
                elif b'CGPADDR' in msg:
                    return self.read_ip(str(msg))
        return False 

    def read_ip(self,msg):
        try:
            start = msg.index( "\"" ) + len( "," )
            end = msg.index( "\"", start )
            self.lte_ip = msg[start:end]
        except Exception as e:
            logging.warning("warning reading lte IP: {}".format(e)) 
            self.lte_ip = -1
                        
        logging.debug("LTE IP: {}".format(self.lte_ip))    

    def read_status(self,msg):
        try:
            start = msg.index( "," ) + len( "," )
            end = msg.index( "\\", start )
            self.lte_status = int(msg[start:end])
        except Exception as e:
            logging.warning("warning reading status: {}".format(e)) 
                        
        logging.info("LTE status: {}".format(self.lte_status)) 

    def read_rssi(self,msg):
        try:
            start = msg.index( ":" ) + len( ":" )
            end = msg.index( ",", start )
            self.raw_rssi = msg[start:end]
        except Exception as e:
            self.raw_rssi = 99
            logging.warning("warning reading rssi: {}".format(e)) 
                        
        logging.debug("Raw RSSI: {}".format(self.raw_rssi)) 
        return self.rssi_convert(int(self.raw_rssi))    
        
    def rssi_convert(self, rssi_raw):    
        if rssi_raw == 0:
            rssi = -113
        elif rssi_raw == 1:
            rssi = -111    
        elif rssi_raw >= 2 and rssi_raw <= 30:
            rssi = (2*rssi_raw)-113
        elif rssi_raw == 31:
            rssi = -51
        elif rssi_raw == 99:
            rssi = 0
        elif rssi_raw == 100:
            rssi = -116
        elif rssi_raw == 101:
            rssi = -115   
        elif rssi_raw >= 102 and rssi_raw <= 190:
            rssi = 76-rssi_raw
        elif rssi_raw == 191:
            rssi = -25
        else:
            rssi = 0         
        logging.debug("Converted RSSI: {}\n".format(rssi))  
        return rssi   
        
    def close_serial(self):
        self.serial.close()    
        
    def get_interface(self):
        try:
            self.net_interface = ConfigIni().get_ipconfig_net_dev()
            logging.debug("Network interface-> {} : {}".format("net_dev", self.net_interface))
        except Exception as e:
            logging.warning("Error reading network interface: {}".format(e))

    def lte_timeout_check(self):
        self.lte_restart_cnt += 1
        logging.warning("LTE not connected {}/10".format(self.lte_restart_cnt))
        if self.lte_restart_cnt >= 30:
            logging.warning("Restarting ppp0 interface")
            self.tx_at_command("reset")
            self.lte_restart_cnt = 0
            self.serial.close()
            time.sleep(30)
            os.system("sudo shutdown -r now") 

    def lte_ip_valid(self):
        try:
            ipaddress.ip_address(self.lte_ip) 
            if self.lte_ip.startswith("0.0") or self.lte_ip.startswith("0:0"):
                return False
            else:
                return True
        except Exception as e:
            logging.warning("IP não recebido".format(e))
            return False
        
    def update_rssi(self):
        try:
            if "ppp" in self.net_interface: 
                logging.debug("| ----Checking RSSI LTE---- |")
                self.connect_serial()
                
                self.tx_at_command("rssi")   
                self.rssi_hub = self.rx_at_command()
                web_interface.update_web_rssi(int(self.rssi_hub))

                time.sleep(3)

                self.tx_at_command("status")
                self.rx_at_command()

                time.sleep(3)

                self.tx_at_command("ip")
                self.rx_at_command()

                if not self.lte_status in [1,5] or not self.lte_ip_valid():
                    self.lte_timeout_check() 
                else:
                    self.lte_restart_cnt = 0    
                    self.hub_restart_cnt = 0           

                self.close_serial()
            elif "wlan" in self.net_interface:
                rssi_msg = check_output(["/sbin/iw wlan0 station dump | grep signal; true"], shell=True)
                rssi_str= str(rssi_msg)
                start = rssi_str.index( " \\t" ) + len( " \\t" )
                end = rssi_str.index( " d", start )
                self.rssi_hub  = rssi_str[start:end]
                web_interface.update_web_rssi(int(self.rssi_hub))
            else:
                web_interface.update_web_rssi(0)    
                         
        except Exception as e:    
            logging.warning("Error reading rssi: {}".format(e)) 
            web_interface.update_web_rssi(0)

           
    def start(self):
        self.get_interface()
        self.timer= multitimer.MultiTimer(interval=55, function=self.update_rssi, count=-1, runonstart=True)
        self.timer.start()