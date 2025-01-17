import zmq
import time
import struct

class FwlVirtual(object):
    def __init__(self): 
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
            'C_CMD':{
                'new_filter_list' : 0,
                'message_to_send': 1,
                'server_status' : 3,
                },
            'SIZE_MSG':{
                'full' : 21,
                'empty' : 17,
                'short' : 7
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
        
        self.sensor_zid = 1
        self.msg_num = 10
        #self.sensor_pid = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        self.sensor_pid = [35,0,75,0,25,80,66,75,48,55,54,32]
        self.vib_x_rms = 1
        self.vib_x_max = 1
        self.vib_z_rms = 1
        self.vib_z_max = 1
        self.temp = 1
        self.bat = 1
        self.num_beacons = 20

    def init_zmq(self):          
        self.ctx = zmq.Context.instance()
        self.sock_pub = self.ctx.socket(zmq.PUB)
        self.sock_pub.bind("tcp://*:5556")
        
        time.sleep(1)
        
        self.sock_sub = self.ctx.socket(zmq.SUB)
        self.sock_sub.connect("tcp://127.0.0.1:5555")
        self.sock_sub.setsockopt_string(zmq.SUBSCRIBE,"") 
               
    def publish_zmq(self, msg):
        self.sock_pub.send(msg)
        
    def receive_zmq(self):
        return self.sock_sub.recv()       
    
    def receive_zmq_non_block(self):
        return self.sock_sub.recv(zmq.NOBLOCK)    
    
    def print_msg(self, title, msg):  
        print(title + ": ", end='')
        for i in range(0, len(msg)):
            print(msg[i], end=' ')
        print()    
      
    def send_global_beacon(self, vib_x_rms, vib_x_max, vib_z_rms, vib_z_max, temp, bat, sensor_zid, num_beacons, *pid):
        msg = struct.pack('<B12BLHLHHHBB', self.const['RF_CMD']['beacon_global_data'], *pid,
                          vib_x_rms, vib_x_max, vib_z_rms, vib_z_max, temp, bat, sensor_zid, num_beacons)
        self.publish_zmq(msg)       
        self.print_msg("Sending Global Beacon", msg)   
    
    def send_seg_waveform(self, wave_id, zid, seg_id, *data):
        msg = struct.pack('<BBBHH110B', wave_id, zid, 112, seg_id, seg_id, *data)
        self.publish_zmq(msg)       
        self.print_msg("Sending Waveform " + str(seg_id), msg)
        
    def send_audio_waveform(self, zid, *data):
        max_segs = self.get_waveform_num_segs(self.const['RF_CMD']['data_seg_aud'])
        for seg_id in range(0, max_segs, 1):
            data = [1] * 110
            self.send_seg_waveform(self.const['RF_CMD']['data_seg_aud'], zid, seg_id, *data)
            seg_id += 1
 
    def send_vib_waveform(self, zid, *data):
        max_segs = self.get_waveform_num_segs(self.const['RF_CMD']['data_seg_vib'])
        for seg_id in range(0, max_segs, 1):
            data = [2] * 110
            self.send_seg_waveform(self.const['RF_CMD']['data_seg_vib'], zid, seg_id, *data)
            seg_id += 1
                   
    def get_waveform_num_segs(self, cmd):
        if cmd == self.const['RF_CMD']['data_seg_vib']:
            if self.const['SAMPLE_SIZE']['vib'] % 56 == 0:
                segs = int(self.const['SAMPLE_SIZE']['vib'] * 1000 / 56)
            else:
                segs = int((self.const['SAMPLE_SIZE']['vib'] * 1000 / 56) + 1)
        elif cmd == self.const['RF_CMD']['data_seg_aud']:
            if self.const['SAMPLE_SIZE']['aud'] % 56 == 0:
                segs = int(self.const['SAMPLE_SIZE']['aud'] * 1000 / 56)
            else:
                segs = int((self.const['SAMPLE_SIZE']['aud'] * 1000 / 56) + 1)    
        return segs 
                 
        
    def run(self):
        self.init_zmq()
        time.sleep(1)
        
        self.send_global_beacon(self.vib_x_rms, self.vib_x_max, self.vib_z_rms, self.vib_z_max, self.temp, self.bat, self.sensor_zid, self.num_beacons, *self.sensor_pid)                
        msg = self.receive_zmq()
        self.print_msg("Received", msg)
        time.sleep(1)
        
        self.send_vib_waveform(self.sensor_zid)
        msg = self.receive_zmq()
        self.print_msg("Received", msg)
        time.sleep(1)
        
        self.send_audio_waveform(self.sensor_zid)
        msg = self.receive_zmq()
        self.print_msg("Received", msg)
        time.sleep(1)

if __name__ == '__main__':
    fwl = FwlVirtual()
    fwl.run()

