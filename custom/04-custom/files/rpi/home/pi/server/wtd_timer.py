import multitimer
import os_mng
from subprocess import check_output
from logging_conf import *
from read_config_ini import ConfigIni

class SensorWtdTimer(object):
    
    _instance = None
    _init = None
    
    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._init is None:
            self._init = True
            self.timer_wtd = multitimer.MultiTimer(interval=60, function=self.wtd_timeout, count=-1, runonstart=False)
            self.timer_full_msg = {'cnt':0 , 'timeout': 30}
            self.timer_server_queue = {'cnt':0 , 'timeout': 30} 
       
    def init_wtd_timer(self):
        self.get_wtd_time_from_file()
        self.timer_wtd.start()

    def restart_wtd_timer_full_msg (self):
        self.timer_full_msg['cnt'] = 0
        
    def restart_wtd_timer_server_queue (self):
        self.timer_server_queue['cnt'] = 0    

    def wtd_timeout(self):
        self.timer_full_msg['cnt'] += 1
        self.timer_server_queue['cnt'] += 1
        
        if self.timer_full_msg['cnt'] >= self.timer_full_msg['timeout'] or self.timer_server_queue['cnt'] >= self.timer_server_queue['timeout']:
            logging.warning("Watchdog Timeout")
            os_mng.reboot_system()
    
    def get_wtd_time_from_file(self):
        try:
            self.timer_full_msg['timeout'] = int(ConfigIni().get_server_wtd_full_msg())
            self.timer_server_queue['timeout'] = int(ConfigIni().get_server_wtd_server_queue())
        except Exception:
            logging.warning("Error reading configuration file")
        else:
            logging.info("Watchdog Complete Message: {} minutes".format(str(self.timer_full_msg['timeout'])))
            logging.info("Watchdog Server Queue: {} minutes".format(str(self.timer_server_queue['timeout'])))      
