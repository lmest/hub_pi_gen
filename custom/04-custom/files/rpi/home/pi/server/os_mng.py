import os
import logging
from get_rssi import GetRSSI

def restart_radio_script():
    logging.info("Restarting radio script")
    os.system("sudo killall -9 fwl_hub")

def reboot_system():
    GetRSSI().set_modem_online_state(False)
    logging.info("Rebooting system")
    os.system("sudo shutdown -r now")

def halt_system():
    GetRSSI().set_modem_online_state(False)
    logging.info("Halting system")
    os.system("sudo shutdown -h now")
