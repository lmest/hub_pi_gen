active_sensors_dict = dict()

def add_list_sensor(sensor_zid, sensor_pid):
    active_sensors_dict[sensor_zid] = sensor_pid

def get_pid(sensor_zid):
    sensor_pid = -1
    if sensor_zid in active_sensors_dict:
        sensor_pid = active_sensors_dict[sensor_zid]
  
    return sensor_pid

def get_pid_str(sensor_zid):
    pid_str = ''
    sensor_pid = get_pid(sensor_zid)
    if sensor_pid != -1:
        for index in range(12):
            pid_str = pid_str + str(sensor_pid[index])
      
    return pid_str

def get_pid_str_from_bytes(pid_bytes):
    pid_str = ''
    if len(pid_bytes) == 12:
        for index in range(12):
            pid_str = pid_str + str(pid_bytes[index])
      
    return pid_str

def check_sensor_in_list(sensor_zid):
    return sensor_zid in active_sensors_dict