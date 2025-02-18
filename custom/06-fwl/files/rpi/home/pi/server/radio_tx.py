import zmq
import time
import struct
import sensors_id_dict
from logging_conf import *
from json_tricks import dumps
from threading import *

class RadioTx():
    
    _instance = None
    _init = None
    
    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):  
        self.const = {
            'RF_CMD':{
                'beacon_global_data' : 1,
                'beacon' : 2,
                'data_req': 3,
                'data_seg_vib' : 4,
                'data_seg_aud': 5,
                'data_check_vib' : 6,
                'data_check_aud' : 7,
                'zigbee_checkin_confirm' : 20
                }, 
            'C_CMD':{
                'new_filter_list' : 0,
                'message_to_send': 1,
                'server_status' : 3
                },
            'SIZE_MSG':{
                'full' : 21,
                'empty' : 17,
                'short' : 7,
                'zigbee_update_req' : 21,
                'zigbee_checkin_confirm' : 13
                },     
            'SAMPLE_RATE':{
                'aud' : 25,
                'vib' : 25
                },
            'SAMPLE_SIZE':{
                'aud' : 50,
                'vib' : 100                
                },
            'DATA_SEG_MSG_SIZE' : 117
            }
        
        if self._init is None:
            self._init = True
            self.msg_num = 0  
            self.sema = Semaphore(1)
        
    def init_zmq(self):    
        self.ctx = zmq.Context.instance()
        self.sock_pub = self.ctx.socket(zmq.PUB)
        self.sock_pub.bind("tcp://*:5555")
        
        time.sleep(1)
        
        self.sock_sub = self.ctx.socket(zmq.SUB)
        self.sock_sub.connect("tcp://127.0.0.1:5556")
        self.sock_sub.setsockopt_string(zmq.SUBSCRIBE,"") 
        
        time.sleep(1)
        
        self.sock_web_pub = self.ctx.socket(zmq.PUB)
        self.sock_web_pub.bind("tcp://*:5557")
    
    def close_zmq(self):
        self.sock_pub.close()
        self.sock_sub.close()
        self.ctx.term()
        
    def receive_zmq(self):
        return self.sock_sub.recv()   
    
    def cnt_msg_num(self):
        self.msg_num += 1
        if self.msg_num > 255:
            self.msg_num = 0
            
    def print_message(self, title, msg):
        print(title, end='')
        for x in range(0, len(msg)):
            print(msg[x], " ", end='')
        print("")

    def __protected_pub_send(self,msg):
        self.sema.acquire()
        self.sock_pub.send(msg)
        self.sema.release()

    def send_server_status(self, status):
        msg_start = struct.pack("<BB", self.const['C_CMD']['server_status'], status)
        try:
            self.__protected_pub_send(msg_start)
        except Exception as e:
            logging.error("pub send error:" + str(e))
        else:
            logging.info("Radio sync message sent")
        self.cnt_msg_num()

    def fwl_send_data_request(self, zid, time2wait, flag):
        if time2wait > 255:
            time2wait = 255
            logging.info("Time to wait {} exceed 255".format(time2wait))
            
        msg_data_request = struct.pack("<BBBBBB12BHBBBBB", self.const['C_CMD']['message_to_send'], zid, self.msg_num, self.const['SIZE_MSG']['full'], self.const['RF_CMD']['data_req'],
                                        time2wait, *struct.pack('<12B', *sensors_id_dict.get_pid(zid)),
                                        zid, flag, self.const['SAMPLE_RATE']['vib'], self.const['SAMPLE_SIZE']['vib'], self.const['SAMPLE_RATE']['aud'], self.const['SAMPLE_SIZE']['aud'])
        self.__protected_pub_send(msg_data_request)
        self.cnt_msg_num()
        #self.print_message("| Data RQ: ", msg_data_request)

    def fwl_send_data_request_empty(self, zid):
        msg_data_request_empty = struct.pack("<BBBBBB12BHB", self.const['C_CMD']['message_to_send'], zid, self.msg_num, self.const['SIZE_MSG']['empty'], self.const['RF_CMD']['data_req'],
                                            0, *struct.pack('<12B', *sensors_id_dict.get_pid(zid)), zid, 0)
        self.__protected_pub_send(msg_data_request_empty)
        self.cnt_msg_num()
        #self.print_message("| Empty RQ: ", msg_data_request_empty)

    def fwl_send_data_request_short(self, zid, time2wait, flag):
        if time2wait > 255:
            time2wait = 255
            logging.info("Time to wait {} exceed 255".format(time2wait))
        
        msg_data_request_short = struct.pack("<BBBBBBBBBBB", self.const['C_CMD']['message_to_send'], zid, self.msg_num, self.const['SIZE_MSG']['short'],
                                            self.const['RF_CMD']['data_req'], time2wait, flag, self.const['SAMPLE_RATE']['vib'], self.const['SAMPLE_SIZE']['vib'],
                                            self.const['SAMPLE_RATE']['aud'], self.const['SAMPLE_SIZE']['aud'])
        self.__protected_pub_send(msg_data_request_short)
        self.cnt_msg_num()
        #self.print_message("| Short RQ: ", msg_data_request_short)

    def fwl_send_data_data_check(self, command, zid, status, msg_index):
        msg_data_check = struct.pack("<BBBBBBH", self.const['C_CMD']['message_to_send'], zid, self.msg_num, 4, command, status, msg_index)
        self.__protected_pub_send(msg_data_check)
        self.cnt_msg_num()         
        
    def send_update_web_server(self, ip_lte, rssi, q_counter, num_beacons):
        data = {'ip_lte' : ip_lte,
                'rssi' : rssi,
                'q_counter' : q_counter,
                'num_beacons' : num_beacons}
        
        self.sock_web_pub.send_string(dumps(data))
        
    def bci_send_rtc_config_request(self, zid, rtc):
        time2wait = 0
        flag = 8
        
        msg_data_request = struct.pack("<BBBBBB12BHBB", self.const['C_CMD']['message_to_send'], zid, self.msg_num, self.const['SIZE_MSG']['full'], self.const['RF_CMD']['data_req'],
                                        time2wait, *struct.pack('<12B', *sensors_id_dict.get_pid(zid)), zid, flag, rtc)
        self.__protected_pub_send(msg_data_request)
        self.cnt_msg_num()
        self.print_message("| Data RQ: ", msg_data_request)
    
    def zigbee_request_network_update(self, zid, new_channel, new_panid, checkin_timeout_min):
        time2wait = 0
        flag = 16
        
        msg_data_request = struct.pack("<BBBBBB12BHBBHB", self.const['C_CMD']['message_to_send'], zid, self.msg_num, self.const['SIZE_MSG']['zigbee_update_req'], 
                                        self.const['RF_CMD']['data_req'], time2wait, *struct.pack('<12B', *sensors_id_dict.get_pid(zid)), zid, flag, new_channel, new_panid, checkin_timeout_min)
        self.__protected_pub_send(msg_data_request)
        self.cnt_msg_num()
        self.print_message("| Zigbee Network Update RQ: ", msg_data_request)        
        
    def zigbee_checkin_confirm(self, zid):       
        msg_data_request = struct.pack("<BBBBB12B", self.const['C_CMD']['message_to_send'], zid, self.msg_num, self.const['SIZE_MSG']['zigbee_checkin_confirm'], 
                                        self.const['RF_CMD']['zigbee_checkin_confirm'], *struct.pack('<12B', *sensors_id_dict.get_pid(zid)))
        self.__protected_pub_send(msg_data_request)
        self.cnt_msg_num()
        self.print_message("| Zigbee Network Update RQ: ", msg_data_request)     