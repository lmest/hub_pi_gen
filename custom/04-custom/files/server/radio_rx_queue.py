from queue import Queue
import multitimer
from wtd_timer import restart_programs
from logging_conf import *

class RadioRxQueue(object):
    def __init__(self):
        self.q = Queue(maxsize=100)
        self.timer = multitimer.MultiTimer(interval=100, function=self.timeout_function, count=1, runonstart=False)
        self.timer_zid = 0
        self.num_timeouts = 0
        self.const = {
            'RF_CMD':{
                'beacon_global_data' : 1,
                'beacon' : 2,
                'data_req': 3,
                'data_seg_vib' : 4,
                'data_seg_aud': 5,
                'data_check_vib' : 6,
                'data_check_aud' : 7
                },
            'transmission_time' : 60,
            'timout_time' : 120,
            'max_timouts_restart' : 100            
        }
        self.timeout_flag = False

    def put_data_queue(self, sensor_id):
        self.q.put(sensor_id)
        logging.info("Adding sensor in Queue")
        self.print_current_queue()            

    def remove_data_queue(self):
        self.q.get_nowait()
        logging.info("Removing sensor from Queue")
        self.print_current_queue()            

    def get_data_queue(self, sensor_id):
        if not self.q.empty():
            if self.is_sensor_in_queue(sensor_id):
                self.remove_data_queue()
                self.timer.stop()
                self.timer_zid = 0 
                if not self.q.empty():
                    self.set_timer(self.const['timout_time'], self.q.queue[0])

    def is_sensor_in_queue(self, sensor_id):
        return sensor_id in list(self.q.queue)

    def set_timer(self, timeout, sensor_id):
        self.timer_zid = sensor_id
        self.timer.stop()
        self.timer.interval = timeout
        self.timer.start()
        logging.info("Timer set - Sensor ID: {} | Timout: {}s".format(sensor_id, timeout))
    
    def new_timer(self, sensor_id):
        if sensor_id != self.timer_zid:
            self.set_timer(self.const['timout_time'], sensor_id)     
        else:
            logging.warning("New timer could not be set. Timer for sensor ID:{} already exists".format(sensor_id))                      

    def timeout_function(self):
        if self.is_sensor_in_queue(self.timer_zid):
            self.get_data_queue(self.timer_zid)
            self.num_timeouts += 1
            self.timeout_flag = True
            self.print_current_queue()
            self.timer_zid = 0
            logging.warning("Timout number: {} / {}".format(self.num_timeouts, self.const['max_timouts_restart']))
            if self.num_timeouts >= self.const['max_timouts_restart']:
                restart_programs()
    
    def print_current_queue(self):            
        logging.info("Current Queue: {}".format(self.q.queue))
        
    def get_queue_str(self):
        return str(self.q.queue)

    def timeout_detected(self):
        if self.timeout_flag == True:
            self.timeout_flag = False
            return True
        else:
            return False        
    
    def queue_is_empty(self):
        return self.q.empty()
    
    def queue_first(self, sensor_id):
        return self.q.queue[0] == sensor_id
    
    def sensor_in_queue(self, sensor_id):
        return sensor_id in list(self.q.queue)
    
    def get_queue_size(self):
        return len(self.q.queue)
    
    def get_queue_index(self, sensor_id):
        return self.q.queue.index(sensor_id)