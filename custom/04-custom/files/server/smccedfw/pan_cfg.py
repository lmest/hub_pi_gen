from threading import *
from logging_conf import *

LIST_ERROR = -1
LIST_OK = 0
UPADATE_REQ = True
NO_REQ = False

class PanCfgReq():
    
    _instance = None
    _init = None
    
    
    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance
    

    def __init__(self):  
        self.req_list = dict()
        self.hub_id = 0
        self.obj_sem = Semaphore(1)
        self.timer_list = []
        

    def check_list(self, sensor_id):
        self.obj_sem.acquire()
        if sensor_id in self.req_list:
            check_return = UPADATE_REQ
        else:
            check_return = NO_REQ
        self.obj_sem.release()
        return check_return


    def remove_list_item(self, sensor_id):
        self.obj_sem.acquire()
       
        if sensor_id in self.timer_list:
            self.timer_list.remove(sensor_id)
            
        if sensor_id in self.req_list:
            del self.req_list[sensor_id]
            remove_status = LIST_OK       
        else:
            remove_status = LIST_ERROR
        
        self.obj_sem.release()
        status_str = {LIST_OK: "OK", LIST_ERROR: "ERROR"}
        logging.info("Pan CFG -> Removing sensor_id: {} | status:{}".format(sensor_id, status_str[remove_status])) 
        return remove_status


    def add_list_item(self, sensor_id_str, channel, panid, timeout=20):
        self.obj_sem.acquire()
        self.req_list[sensor_id_str] = [channel, panid, timeout]
        self.start_checkin_timer(sensor_id_str, timeout)
        self.obj_sem.release()


    def get_list_cnt(self, sensor_id):
        self.obj_sem.acquire()
        if sensor_id in self.req_list:
            list_cnt = self.req_list[sensor_id]
        else:
            list_cnt = LIST_ERROR
        self.obj_sem.release()
        return list_cnt
    

    def get_channel(self, sensor_id):
        self.obj_sem.acquire()
        if sensor_id in self.req_list:
            channel = self.req_list[sensor_id][0]
        else:
            channel = LIST_ERROR
        self.obj_sem.release()
        return channel
    
    
    def get_pan_id(self, sensor_id):
        self.obj_sem.acquire()
        if sensor_id in self.req_list:
            panid = self.req_list[sensor_id][1]
        else:
            panid = LIST_ERROR
        self.obj_sem.release()
        return panid
    

    def get_timeout(self, sensor_id):
        self.obj_sem.acquire()
        if sensor_id in self.req_list:
            timeout = self.req_list[sensor_id][2]
        else:
            timeout = LIST_ERROR
        self.obj_sem.release()
        return timeout    
    
    
    def get_req_list(self):
        return self.req_list  
    
    
    def start_checkin_timer(self, sensor_id, timeout):
        if sensor_id in self.timer_list:
            logging.info("Pan CFG -> Timer for sensor_id: {} already created".format(sensor_id))
        else:
            t = Timer(timeout*60, self.remove_list_item, [sensor_id])
            t.start() 
            logging.info("Pan CFG -> Starting timer for sensor_id: {} with timeout: {} minutes".format(sensor_id, timeout))
            self.timer_list.append(sensor_id)


class PanCfgConfirmChange(object):

    def __init__(self, hub_id, sensor_id):
        self.hub_id = hub_id
        self.sensor_id = sensor_id
