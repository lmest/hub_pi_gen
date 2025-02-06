import os

def configure_wifi_enterprise(ssid, identity, password):
    config_lines = [
        'country=BR',
        'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev',
        'ap_scan=1',
        'update_config=1',
        '\n',
        'network={',
        '\tssid="{}"'.format(ssid),
        '\tidentity="{}"'.format(identity),
        '\tpassword="{}"'.format(password),
        '\tpriority=1',
        '\tproto=RSN',
        '\tkey_mgmt=WPA-EAP',
        '\tpairwise=CCMP',
        '\tauth_alg=OPEN',
        '\teap=PEAP',
        '\tphase1="peaplabel=0"',
        '\tphase2="auth=MSCHAPV2"',
        '}'
        ]
    config = '\n'.join(config_lines)
    print(config)
    
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as wifi:
        wifi.write(config)
    
    print("Wifi config added. Refreshing wlan0.\n")
    os.popen("sudo wpa_cli -i wlan0 reconfigure")
    
def configure_wifi_personal(ssid, password):
    config_lines = [
        'country=BR',
        'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev',
        'ap_scan=1',
        'update_config=1',
        '\n',
        'network={',
        '\tssid="{}"'.format(ssid),
        '\tpsk="{}"'.format(password),
        '\tscan_ssid=1',
        '}'
        ]
    config = '\n'.join(config_lines)
    print(config)
    
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as wifi:
        wifi.write(config)
    
    print("Wifi config added. Refreshing wlan0.\n")
    os.popen("sudo wpa_cli -i wlan0 reconfigure")    
    
