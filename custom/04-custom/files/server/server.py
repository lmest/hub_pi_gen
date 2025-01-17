import struct
import time
import smccedfw.req_recv as req_recv
import sensors_id_dict 
from fwl_data_process import FwlDataProcess 
from radio_tx import RadioTx 
from get_server_status import Get_ServerStatus
from logging_conf import *
import web_interface 
from smccedfw.bci import BCI
from smccedfw.pan_cfg import PanCfgReq, PanCfgConfirmChange
import dashboard.send_log as dashboard
from smccedfw.amqp_publish import publish_amqp
import bridge_graph

class Server(object):  
    def __init__(self, server_status):      
        self.const = {
            'RF_CMD':{
                'beacon_global_data' : 1,
                'beacon' : 2,
                'data_req': 3,
                'data_seg_vib' : 4,
                'data_seg_aud': 5,
                'data_check_vib' : 6,
                'data_check_aud' : 7,
                'beacon_bci' : 17
                }, 
            'STATUS' : {
                'ok': 0,
                'error' : 1
            },
            'REQ' : {
                'waveform' : 0,
                'globals' : 1,
                'no' : 2
            },
            'data_seg_msg_size' : 117,
        }        
        self.cmd = 0
        self.msg_received = 0
        self.sensor_zid = 0
        self.fwl_sensor_data = FwlDataProcess()
        self.send_data = RadioTx()
        self.func_list = {1: self.read_global_beacon_fwl,
                          2: self.read_beacon_fwl,
                          4: self.read_data_seg_fwl,
                          5: self.read_data_seg_fwl,
                          11: self.read_send_confirmation,
                          12: server_status.set_reply_status,
                          17: self.read_beacon_bci,
                          19: self.read_zigbee_network_checkin}
        self.bci = BCI()
        self.pan_cfg = PanCfgReq()
               
            
    def read_send_confirmation(self): 
        status = msg_numb = 0
        confirmation_status = ['OK', 'ERROR']
   
        try:
            (self.cmd, self.sensor_zid, msg_numb, status) = struct.unpack('<BBBB', self.msg_received)
        except struct.error as e:
            logging.warning("Unpack Error Confirmation: {}".format(e))
        else:
            if status <= 1:
                logging.info("Sensor Confirmation - ZID: {} | Status: {} | Msg Number: {}".format(self.sensor_zid, confirmation_status[status], msg_numb))
                dashboard.PubLog().send_request_ack(sensors_id_dict.get_pid_str(self.sensor_zid), status)
                if status == self.const['STATUS']['error']:
                        self.fwl_sensor_data.check_seg_restart()  
            else:
                logging.warning("Invalid Status: {}".format(status))
                  
                  
    def read_beacon_bci(self):
        try:
            (self.cmd, *pid, press, temp, bat, self.sensor_zid, num_beacons) = struct.unpack('<B12BHHHBB', self.msg_received)
            press=float(press/10**4)
            temp=float(temp/10**4)
            bat=float(bat/10**4)
            web_interface.update_num_beacons(int(num_beacons))
        except struct.error as e:
            logging.warning("Unpack Error BCI Beacon: {}".format(e))            
        else:
            logging.info("Beacon BCI Received | ID:{} | ZID: {}".format(sensors_id_dict.get_pid_str_from_bytes(pid), self.sensor_zid))
            logging.info("Pressure: {} | Temperature: {} | Battery: {}".format(press, temp, bat))    
            sensors_id_dict.add_list_sensor(self.sensor_zid, pid) 
            self.bci.send_data_server(pid, press, temp)
            self.send_data.bci_send_rtc_config_request(self.sensor_zid, 66) 
            self.send_data.print_message("| BCI Beacon: ", self.msg_received)
            
    def read_zigbee_network_checkin(self):
        try:
            (self.cmd, *pid, self.sensor_zid) = struct.unpack('<B12BB', self.msg_received)
        except struct.error as e:
            logging.warning("Unpack Error Zigbee Checkin: {}".format(e))
        else:
            sensors_id_dict.add_list_sensor(self.sensor_zid, pid) 
            self.send_data.zigbee_checkin_confirm(self.sensor_zid)      
            pid_str = sensors_id_dict.get_pid_str_from_bytes(pid)
            hub_id_str = req_recv.get_hub_id()  
            self.pan_cfg_confirm_change = PanCfgConfirmChange(pid_str, hub_id_str)
            publish_amqp(self.pan_cfg_confirm_change)
            logging.info("Zigbee Network Check-in | ID:{} | ZID: {} | HUB: {}".format(pid_str, self.sensor_zid, hub_id_str))
            
    def zigbee_update_is_required(self):
        return self.pan_cfg.check_list(sensors_id_dict.get_pid_str(self.sensor_zid))   
    
    def zigbee_request_network_update(self):        
        logging.info("Zigbee Update Required!")
        ch = self.pan_cfg.get_channel(sensors_id_dict.get_pid_str(self.sensor_zid))
        pan = self.pan_cfg.get_pan_id(sensors_id_dict.get_pid_str(self.sensor_zid))
        timeout = self.pan_cfg.get_timeout(sensors_id_dict.get_pid_str(self.sensor_zid))
        logging.info("Channel: {} | Panid: {} | Timeout: {}".format(ch, pan, timeout))
        logging.info("Sensor ID: {}".format(sensors_id_dict.get_pid_str(self.sensor_zid)))
        if ch != -1 and pan != -1:
            self.send_data.zigbee_request_network_update(self.sensor_zid, ch, pan, timeout)
        else:
            logging.warning("Error getting channel and panid")
            
    def read_global_beacon_fwl(self):
        vib_x_rms = vib_x_max = vib_z_rms = vib_z_max = temp = bat = 0
        pid = []

        try:
            (self.cmd, *pid, vib_x_rms, vib_x_max, vib_z_rms, vib_z_max, temp, bat, self.sensor_zid, num_beacons) = struct.unpack('<B12BLHLHHHBB', self.msg_received)
            vib_x_rms=float(vib_x_rms/10**4)
            vib_x_max=float(vib_x_max/10**4)
            vib_z_rms=float(vib_z_rms/10**4)
            vib_z_max=float(vib_z_max/10**4)
            bat=float(bat/10**4)
            self.fwl_sensor_data.set_globals_var(self.sensor_zid, vib_x_rms, vib_x_max, vib_z_rms, vib_z_max, temp, bat, num_beacons)
            web_interface.update_num_beacons(int(num_beacons))
        except struct.error as e:
            logging.warning("Unpack Error Global Beacon: {}".format(e))
            logging.warning("Msg Received: {}".format(self.msg_received))
        else:
            sensors_id_dict.add_list_sensor(self.sensor_zid, pid)                        
            print("")
            logging.info("Beacon Global Received | ID:{} | ZID: {}".format(sensors_id_dict.get_pid_str(self.sensor_zid), self.sensor_zid))
            logging.info("Vib X rms: {} | Vib X max: {} || Vib Z rms: {} | Vib Z max: {}".format(vib_x_rms, vib_x_max, vib_z_rms, vib_z_max))
            logging.info("Temperature: {} | Battery: {}".format(float(temp/10**4), float(bat/10**4)))
            
            dashboard.PubLog().send_beacon_fwl(sensors_id_dict.get_pid_str(self.sensor_zid), vib_x_rms, vib_x_max, vib_z_rms, vib_z_max, temp, bat, self.sensor_zid, num_beacons)
            
            if self.zigbee_update_is_required():
                self.zigbee_request_network_update()
            else:            
                check_sensor_list = req_recv.check_list(sensors_id_dict.get_pid_str(self.sensor_zid))
                
                if(bridge_graph.bypass_server_req == 1):
                    check_sensor_list = self.const['REQ']['waveform']
            
                if check_sensor_list == self.const['REQ']['waveform']:
                    self.fwl_sensor_data.read_beacon(self.cmd, self.sensor_zid)
                elif check_sensor_list == self.const['REQ']['globals']:
                    self.send_data.fwl_send_data_request_empty(self.sensor_zid)                
                    self.fwl_sensor_data.send_data_global_server(self.sensor_zid)
                    logging.info("Globals Request!")
                    req_recv.remove_list_item(sensors_id_dict.get_pid_str(self.sensor_zid))
                elif check_sensor_list == self.const['REQ']['no']:
                    self.send_data.fwl_send_data_request_empty(self.sensor_zid)
                    logging.info("No request for this sensor!")
                
            
    def read_beacon_fwl(self):
        try:
            (self.cmd, self.sensor_zid) = struct.unpack('<BB', self.msg_received)
        except struct.error as e:
            logging.warning("Unpack Error Beacon: {}".format(e))
        else:
            if sensors_id_dict.check_sensor_in_list(self.sensor_zid):
                logging.info("Beacon Received | ID:{} | ZID: {}".format(sensors_id_dict.get_pid_str(self.sensor_zid), self.sensor_zid))
                self.fwl_sensor_data.read_beacon(self.cmd, self.sensor_zid)
            else:
                logging.info("Beacon -> ZID:{} is not in active list".format(self.sensor_zid))
           
    
    def read_data_seg_fwl(self):
        if len(self.msg_received) == self.const['data_seg_msg_size']:
            self.fwl_sensor_data.read_msg(self.msg_received)
        else:
            logging.warning("Data segment size error")
            
            
    def receive_loop(self):

        while True:
            try:
                self.msg_received = self.send_data.receive_zmq()
            except Exception as e:
                logging.warning(e)
            else:
                self.cmd = self.msg_received[0]
                
                if self.cmd in self.func_list:
                    self.func_list[self.cmd]()                  
                else:
                    self.send_data.print_message("| Invalid Msg: ", self.msg_received)

                self.fwl_sensor_data.check_msg(self.cmd)


if __name__ == '__main__':
    logging.info("Starting Server Manager ...\n\n")
    
    bridge_graph.bridge_init()

    s_data = RadioTx()
    s_data.init_zmq()    
    req_recv.main()
    
    server_status = Get_ServerStatus()
    server_status.start()
    
    time.sleep(5) 
    web_interface.start_web_queue()
    
    dashboard.PubLog().send_script_start_time()
    dashboard.PubLog().send_cpu_temp()
    
    Server(server_status).receive_loop()