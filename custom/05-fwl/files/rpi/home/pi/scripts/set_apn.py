import sys
import os

def process(apn):
    contents = open("/home/pi/scripts/templates/provider","rt").read()
    contents = contents.replace('__APN__',apn)
    open("/home/pi/scripts/provider","wt").write(contents)
    os.system("sudo cp /home/pi/scripts/provider /etc/ppp/peers/provider")
    os.system("rm /home/pi/scripts/provider")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        apn = sys.argv[1].strip()
        if apn:
            process(apn)
        else:
            print(f'{sys.argv[0]} apn')
    else:
        print(f'{sys.argv[0]} apn')
