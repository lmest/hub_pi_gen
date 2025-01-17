import logging
import subprocess
import sys
import time
import os
from subprocess import check_output

STATUS_INIT = 0
STATUS_RUNNING= 1
STATUS_CLOSED = 2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("/home/pi/watchdog/watchdog.log"),
        logging.StreamHandler(sys.stdout),
    ],
    datefmt='%d-%b-%y %H:%M:%S'
)


class ProcessWatcher:
    def __init__(self, max_restart, max_log_size_mb):
        self.max_restart = max_restart
        self.max_log_size_mb = max_log_size_mb
        self.process_var = {
                'Server': {
                    'process_command' : ["/usr/bin/screen -L -Logfile /home/pi/watchdog/screen_server.log -dmS server sudo -E python3 /home/pi/server/server.py; true"], 
                    'restart_num' : 0, 
                    'process_status': STATUS_INIT, 
                    'status' : True,
                    },
                'Radio': {
                    'process_command' : ["/usr/bin/screen -L -Logfile /home/pi/watchdog/screen_radio.log -dmS radio sudo /home/pi/radio/fwl_hub; true"], 
                    'restart_num' : 0, 
                    'process_status' : STATUS_INIT, 
                    'status' : True,
                    },
                'IpConfig': {
                    'process_command' : ["/usr/bin/screen -L -Logfile /home/pi/watchdog/screen_ipconfig.log -dmS ipconfig sudo -E python3 /home/pi/ipconfig.py; true"], 
                    'restart_num' : 0, 
                    'process_status' : STATUS_INIT, 
                    'status' : True,
                    },
                'Web': {
                    'process_command' : ["/usr/bin/screen -L -Logfile /home/pi/watchdog/screen_web.log -dmS web sudo -E python3 /home/pi/webserver/webserver.py; true"], 
                    'restart_num' : 0, 
                    'process_status' : STATUS_INIT, 
                    'status' : True,
                    }                            
                }
        self.logs_name = {"Server": "screen_server.log", "Radio": "screen_radio.log", 
                          "Watchdog": "watchdog.log", "IpConfig": "screen_ipconfig.log",
                          "Web": "screen_web.log"}


        
    def init_proccess_wtd(self):
        logging.info("| Starting Process Watchdog")
        for k in self.process_var:
            if not self.process_is_open(str(k).lower()) and self.process_var[k]['status'] == True:                
                self.open_process(k)
        time.sleep(5)

               

    def check_log_size(self, file_name):
        try:
            if os.path.getsize("/home/pi/watchdog/" + self.logs_name[file_name]) / (1024 * 1024) > self.max_log_size_mb:
                logging.warning("| " + file_name + " Log Limit Size Reached!")
                logging.warning("| Cleaning File\n|")
                open("/home/pi/watchdog/" + self.logs_name[file_name], "w").close()
        except FileNotFoundError:
            logging.info("| File: " + self.logs_name[file_name] + " is empty\n|")


    @staticmethod
    def reboot_system():
        logging.warning("| Restart Limit Reached!")
        logging.warning("| Rebooting System")
        time.sleep(20)
        os.system("sudo shutdown -r now")
           
    def open_process(self, process_key):     
        subprocess.Popen(self.process_var[process_key]['process_command'], shell=True) 
         
    @staticmethod
    def set_led_error():
        subprocess.Popen(["sudo /home/pi/led_reset.sh; true"], shell=True)
        time.sleep(5)

    @staticmethod
    def process_is_open(process_name):
        screen_ls = check_output(["screen -ls; true"], shell=True)
        return process_name in str(screen_ls)
    
    def check_process(self, process_name):
        check_var = self.process_var[process_name]
        
        if self.process_is_open(str(process_name).lower()):
            if check_var['process_status'] != STATUS_RUNNING:
                check_var['process_status'] = STATUS_RUNNING
                logging.info("| " + process_name + " Process Running")
        else:
            check_var['process_status'] = STATUS_CLOSED
            check_var['restart_num'] += 1
            logging.warning("| " + process_name + " Process Closed - Restarting!")
            logging.warning("| " + process_name + " Restart: " + str(check_var['restart_num']) +
                            " | Limit: " + str(self.max_restart))
            if check_var['restart_num'] < self.max_restart:
                self.set_led_error()
                self.open_process(process_name)                
            else:
                self.set_led_error()
                self.reboot_system()
       
        return check_var['process_status'] , check_var['restart_num']    

    def run(self, wait_time):
        while True:
             
            for k in self.process_var:
                if self.process_var[k]['status'] == True:
                    self.check_process(k)
            
            for k in self.logs_name:
                self.check_log_size(k)
            
            time.sleep(wait_time)


if __name__ == '__main__':
    pw = ProcessWatcher(20, 10)
    pw.init_proccess_wtd()
    pw.run(5)
