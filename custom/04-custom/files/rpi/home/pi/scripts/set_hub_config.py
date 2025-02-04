import sys

def process(channel,pan_id,server,port,net_dev,hub_id):
    contents = open("/home/pi/scripts/templates/hub_config.ini","rt").read()
    contents = contents.replace('__CHANNEL__',channel)
    contents = contents.replace('__PAN_ID__',pan_id)
    contents = contents.replace('__SERVER_',server)
    contents = contents.replace('__PORT__',port)
    contents = contents.replace('__NET_DEV__',net_dev)
    contents = contents.replace('__HUB_ID__',hub_id)
    open("/home/pi/hub_config.ini","wt").write(contents)

if __name__ == "__main__":
    if len(sys.argv) > 6:
        channel = sys.argv[1].strip()
        pan_id = sys.argv[2].strip()
        server = sys.argv[3].strip()
        port = sys.argv[4].strip()
        net_dev = sys.argv[5].strip()
        hub_id = sys.argv[6].strip()
        if apn and channel and pan_id and server and port and net_dev and hub_id:
            process(channel,pan_id,server,port,net_dev,hub_id)
        else:
            print(f'{sys.argv[0]} channel pan_id server port eth0|ppp0 hub_id')
    else:
        print(f'{sys.argv[0]} channel pan_id server port eth0|ppp0 hub_id')
