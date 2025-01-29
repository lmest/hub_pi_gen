import struct
import traceback
from logging_conf import *
import numpy as np
from radio_tx import RadioTx 
from wtd_timer import SensorWtdTimer
import sensors_id_dict 
from radio_rx_queue import RadioRxQueue 
from get_rssi import GetRSSI
import web_interface
from smccedfw.requisicao import Sinal
from smccedfw.amqp_publish import publish_amqp
import smccedfw.req_recv as req_recv
import dashboard.send_log as dashboard
import bridge_graph

def print_pck(pack):
    pck = np.frombuffer(pack, dtype=np.uint16, offset=0)/10000
    print(str(pck))


class FwlDataProcess(object):
    
    _instance = None
    _init = None
    
    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance
  
    def __init__(self):       
        self.const = {
            'STATUS' : {
                'ok': 0,
                'error' : 1,
                'wait' : 2
                },
            'MSG_COMPLETE' : {
                'false' : 0,
                'true' : 1
            },
            'TRANSMISSION_MODE' : {
                'transmission' : 0,
                'retransmission' : 1
            },
            'RF_CMD':{
                'beacon_global_data' : 1,
                'beacon' : 2,
                'data_req': 3,
                'data_seg_vib' : 4,
                'data_seg_aud': 5,
                'data_check_vib' : 6,
                'data_check_aud' : 7                
            },
            'SAMPLE_SIZE':{
                'aud' : 50,
                'vib' : 100                
            },
            'SAMPLE_RATE':{
                'aud' : 25,
                'vib' : 25
            },
            'transmission_time' : 60
        }
            
        if self._init is None:
            self._init = True        
            self.status_recv = self.const['STATUS']['ok']
            self.msg_cnt = 0
            self.msg_received = [] * 200
            self.seg_status = self.const['MSG_COMPLETE']['false']
            self.transmission_status = self.const['TRANSMISSION_MODE']['transmission']
            self.vet_seg_error = []
            self.index_vet_error = 0
            self.pack_size = 0
            self.sensor_data = 0#[[0] * 112] * (self.pack_size + 1)
            self.sensor_vib1_data = [[0] * 112] * (self.pack_size + 1)
            self.sensor_vib2_data = [[0] * 112] * (self.pack_size + 1)
            self.sensor_aud_data = [[0] * 112] * (self.pack_size + 1)
            self.data_cmd = 0
            self.zid = 0
            self.new_zid = 0
            self.seg_recv_index = 0
            self.last_seg_recv_index = -1
            self.formatted_data = []
            self.globals = {}
            self.wtd_timer = SensorWtdTimer()
            self.wtd_timer.init_wtd_timer()
            self.print_msg_ret = True
            self.data_type = {4: 'VIB', 5: 'AUD'}
            self.queue_obj = RadioRxQueue()
            self.send_obj = RadioTx()
            self.get_rssi_obj = GetRSSI()
            self.get_rssi_obj.start()
            self.flag_ret_error = False
            self.fwl = Sinal()
        
    def clean_variables(self):
        self.status_recv = self.const['STATUS']['ok']
        self.msg_cnt = 0
        self.msg_received = [] * 200
        self.seg_status = self.const['MSG_COMPLETE']['false']
        self.transmission_status = self.const['TRANSMISSION_MODE']['transmission']
        self.vet_seg_error = []
        self.index_vet_error = 0
        self.seg_recv_index = 0
        self.last_seg_recv_index = -1
        self.print_msg_ret = True
        self.flag_ret_error = False


    def set_globals_var(self, sensor_zid, vib_rms1, vib_max1, vib_rms2, vib_max2, temp, bat, num_beacons):
        self.globals[sensor_zid] = [vib_rms1, vib_max1, vib_rms2, vib_max2, temp, bat, num_beacons]

    def init_var(self, cmd, id):
        self.clean_variables()
        if cmd == self.const['RF_CMD']['data_seg_vib']:
            if self.const['SAMPLE_SIZE']['vib'] % 56 == 0:
                self.pack_size = int(self.const['SAMPLE_SIZE']['vib'] * 1000 / 56)
            else:
                self.pack_size = int((self.const['SAMPLE_SIZE']['vib'] * 1000 / 56) + 1)
        elif cmd == self.const['RF_CMD']['data_seg_aud']:
            if self.const['SAMPLE_SIZE']['aud'] % 56 == 0:
                self.pack_size = int(self.const['SAMPLE_SIZE']['aud'] * 1000 / 56)
            else:
                self.pack_size = int((self.const['SAMPLE_SIZE']['aud'] * 1000 / 56) + 1)

        self.sensor_data = [[0] * 112] * self.pack_size
        self.flag_ret_error = False
        logging.info("Data Segment Init - Sensor ID: {} TYPE: {}".format(id, self.data_type[cmd]))
        
    def read_beacon(self, cmd, sensor_id):
        self.queue_obj.print_current_queue()
        dashboard.PubLog().send_zigbee_queue(self.queue_obj.get_queue_str())
        if self.queue_obj.queue_is_empty() or self.queue_obj.queue_first(sensor_id):
            if not self.queue_obj.sensor_in_queue(sensor_id):
                self.queue_obj.put_data_queue(sensor_id)
            self.queue_obj.new_timer(sensor_id)
            if cmd == self.const['RF_CMD']['beacon_global_data']:
                self.send_obj.fwl_send_data_request(sensor_id, 0, 3)
            elif cmd == self.const['RF_CMD']['beacon']:
                self.send_obj.fwl_send_data_request_short(sensor_id, 0, 3)
        else:
            if not self.queue_obj.sensor_in_queue(sensor_id):
                if cmd == self.const['RF_CMD']['beacon_global_data']:
                    self.send_obj.fwl_send_data_request(sensor_id, self.const['transmission_time'] * (self.queue_obj.get_queue_size()), 3)
                elif cmd == self.const['RF_CMD']['beacon']:
                    self.send_obj.fwl_send_data_request_short(sensor_id, self.const['transmission_time'] * (self.queue_obj.get_queue_size()), 3)
                self.queue_obj.put_data_queue(sensor_id)
            else:
                if cmd == self.const['RF_CMD']['beacon_global_data']:
                    self.send_obj.fwl_send_data_request(sensor_id, self.const['transmission_time'] * (self.queue_obj.get_queue_index(sensor_id)), 3)
                elif cmd == self.const['RF_CMD']['beacon']:
                    self.send_obj.fwl_send_data_request_short(sensor_id, self.const['transmission_time'] * (self.queue_obj.get_queue_index(sensor_id)), 3)

    def read_msg(self, buffer):
        try:
            self.data_cmd = struct.unpack('<B', buffer[0:1])[0]
            self.new_zid = struct.unpack('<B', buffer[1:2])[0]
            self.seg_recv_index = struct.unpack('<H', buffer[3:5])[0]
        except Exception as e:
            logging.warning("Exception Reading Package {}: {}".format(self.seg_recv_index, e))
            print(traceback.format_exc())
        else:                                
            if self.queue_obj.queue_is_empty() or self.queue_obj.queue_first(self.new_zid):                    
                var_clean = False
                
                if self.queue_obj.timeout_detected() or (self.zid == self.new_zid and self.flag_ret_error == True):
                    self.init_var(self.data_cmd, self.new_zid)
                    logging.info("Timeout Detected - Erasing vars")
                    var_clean = True
                    
                self.zid = self.new_zid    
                                    
                if self.transmission_status == self.const['TRANSMISSION_MODE']['transmission']:
                    try:
                        if self.seg_recv_index == 0 and var_clean == False:
                            self.init_var(self.data_cmd,self.zid)
                            
                        if self.seg_recv_index > self.last_seg_recv_index:                     
                            try:                        
                                self.sensor_data[self.seg_recv_index] = struct.unpack('<112s', buffer[5:117])
                            except:  
                                self.init_var(self.data_cmd,self.zid)
                                self.sensor_data[self.seg_recv_index] = struct.unpack('<112s', buffer[5:117])
                            else:  
                                self.last_seg_recv_index = self.seg_recv_index 

                                if self.seg_recv_index != self.msg_cnt:
                                    if self.seg_recv_index > self.msg_cnt:
                                        while self.seg_recv_index != self.msg_cnt:
                                            self.vet_seg_error.append(self.msg_cnt)
                                            self.msg_cnt += 1
                                        self.status_recv = self.const['STATUS']['error']
                                    self.msg_cnt = self.seg_recv_index + 1
                                else:
                                    self.msg_cnt = self.msg_cnt + 1                

                        if self.seg_recv_index + 1 >= self.pack_size:
                            self.seg_status = self.const['MSG_COMPLETE']['true']
                            logging.info("Data Segment End - Sensor ID: {} TYPE: {}".format(self.zid, self.data_type[self.data_cmd]))
                    except Exception as e:
                        logging.warning("Exception Transmission Package {}: {}".format(self.seg_recv_index, e))
                        print(traceback.format_exc())
                        self.init_var(self.data_cmd, self.zid )

                elif self.transmission_status == self.const['TRANSMISSION_MODE']['retransmission']:
                    try:
                        if self.seg_recv_index in self.vet_seg_error:
                            logging.info("Retransmited Package: {}".format(str(self.seg_recv_index)))
                            self.sensor_data[self.seg_recv_index] = struct.unpack('<112s', buffer[5:117])
                            self.vet_seg_error.remove(self.seg_recv_index)
                            
                            #self.send_obj.print_message("RF_CMD_DATA_SEG [" + str(buffer[0]) + " || " + str(self.seg_recv_index) + "]: ", buffer)
                            
                            #pck = [[0] * 112] * (1)
                            #pck[0] = self.sensor_data[self.seg_recv_index]                           
                            #pck1 = self.format_data(pck)                            
                            #pck2 = pck1[0:112]                            
                            #print_pck(pck2)

                            if len(self.vet_seg_error) == 0:
                                logging.info("Retransmission Complete!")
                                self.status_recv = self.const['STATUS']['ok']
                            else:
                                self.status_recv = self.const['STATUS']['error']
                    except Exception as e:
                        logging.warning("Exception Retransmission: {}: {}".format(self.seg_recv_index, e))
                        self.clean_variables()
            else:
                logging.warning("Sensor that is not in the queue tried to send data")
                logging.warning("Sensor: {}  |  Queue:{}".format(self.zid, self.queue_obj.q.queue))
            

    def format_data(self, data):
        self.formatted_data = []
        for x in range(len(data)):
            self.formatted_data.insert(x, data[x][0])
        return b''.join(self.formatted_data)

    def check_msg(self, msg_type):       
        if self.seg_status == self.const['MSG_COMPLETE']['true']:
            if self.status_recv == self.const['STATUS']['ok']:
                self.send_obj.fwl_send_data_data_check(msg_type + 2, self.zid, self.const['STATUS']['ok'], 0)
                logging.info("Message OK! Sensor ID: {} Num Pack: {}\n".format(self.zid, self.msg_cnt - 1))
                try:
                    self.sensor_data = self.format_data(self.sensor_data)
                    if msg_type == self.const['RF_CMD']['data_seg_vib']:
                        self.sensor_vib1_data = struct.unpack('<{}s'.format(100000), self.sensor_data[0:100000])
                        self.sensor_vib2_data = struct.unpack('<{}s'.format(100000), self.sensor_data[100000:200000])
                    elif msg_type == self.const['RF_CMD']['data_seg_aud']:
                        self.sensor_aud_data = self.sensor_data[0:100000]                        
                        self.send_data_server()
                        self.queue_obj.get_data_queue(self.zid)
                        req_recv.remove_list_item(sensors_id_dict.get_pid_str(self.zid))
                    self.clean_variables()
                except Exception as e:
                    self.status_recv = self.const['STATUS']['wait']
                    logging.warning("Error sending data: {}".format(e))
                else:
                    self.wtd_timer.restart_wtd_timer_full_msg()

            elif self.status_recv == self.const['STATUS']['error']:
                self.transmission_status = self.const['TRANSMISSION_MODE']['retransmission']
                if len(self.vet_seg_error) > 0:
                    if self.print_msg_ret:
                        self.send_obj.print_message("|\n| Retransmission Required! \n| Missing Packages: ", self.vet_seg_error)
                        dashboard.PubLog().send_num_retries(sensors_id_dict.get_pid_str(self.zid), len(self.vet_seg_error))
                        self.print_msg_ret = False
                    self.send_obj.fwl_send_data_data_check(msg_type + 2, self.zid, self.const['STATUS']['error'], self.vet_seg_error[self.index_vet_error])
                    self.status_recv = self.const['STATUS']['wait']

    def check_seg_restart(self):
        if self.transmission_status == self.const['TRANSMISSION_MODE']['retransmission']:
            logging.warning("Retransmission Failed!\n| Waiting Data Segment Restart")
            self.flag_ret_error = True
    
    def send_data_server(self):
        dashboard.PubLog().send_waveform_completed(sensors_id_dict.get_pid_str(self.zid))
        self.fwl.set_header(req_recv.get_list_cnt(sensors_id_dict.get_pid_str(self.zid)), struct.pack('<12B', *sensors_id_dict.get_pid(self.zid)),
                                                        req_recv.hub_id, 63, self.const['SAMPLE_RATE']['aud'], self.const['SAMPLE_SIZE']['aud']*1000, self.const['SAMPLE_RATE']['vib'], self.const['SAMPLE_SIZE']['vib']*1000)
        self.fwl.set_sensor_data(self.globals[self.zid], self.get_rssi_obj.rssi_hub , web_interface.get_web_q_counter(),
                                               self.sensor_aud_data, self.sensor_vib2_data[0], self.sensor_vib1_data[0],
                                               len(self.sensor_aud_data), len(self.sensor_vib1_data[0]))
        publish_amqp(self.fwl)
        logging.info("Data Sent!")
        logging.debug(self.fwl)
        self.wtd_timer.restart_wtd_timer_full_msg()
        bridge_graph.save_graph_img(self.fwl.ano, self.fwl.mes, self.fwl.dia, self.fwl.hora, self.fwl.minutos, self.fwl.segundos,
                            self.fwl.waveform_vibracao1, self.fwl.waveform_vibracao2, self.fwl.waveform_audio,
                            sensors_id_dict.get_pid_str(self.zid), bat=self.globals[self.zid][5], temp=self.globals[self.zid][4])

    def send_data_global_server(self, sensor_zid):
        self.fwl.set_header(0, struct.pack('<12B', *sensors_id_dict.get_pid(sensor_zid)),
                                                        req_recv.hub_id, 7, 0, 0, 0, 0)
        self.fwl.set_sensor_data(self.globals[sensor_zid], self.get_rssi_obj.rssi_hub, web_interface.get_web_q_counter(),
                                               struct.pack('<2s', b"00"), struct.pack('<2s', b"00"), struct.pack('<2s', b"00"), 2, 2)
        publish_amqp(self.fwl)
        logging.debug("Globals Sent!")
        self.wtd_timer.restart_wtd_timer_full_msg() 