import os
import logging

def restart_radio_script():
    logging.info("Restarting radio script")
    os.system("sudo killall -9 fwl_hub")

def reboot_system():
    logging.info("Rebooting system")
    os.system("sudo shutdown -r now")