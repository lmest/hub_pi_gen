from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import zmq
from threading import *
import os
import configparser
import multitimer
from datetime import timedelta
import wpa_update as wpa

ctx = zmq.Context.instance()

sock_sub =ctx.socket(zmq.SUB)
sock_sub.setsockopt_string(zmq.SUBSCRIBE,"") 
sock_sub.setsockopt(zmq.CONFLATE, 1)  # last msg only.
sock_sub.connect("tcp://127.0.0.1:5557")

msg_received = {'ip_lte' : 0, 'rssi': 0,
                'q_counter' : 0, 'num_beacons' : 0}

app = Flask(__name__)
app.secret_key = ""
app_user = ""
app_psw = ""

def shutdown_hub():
   os.system("sudo shutdown now") 
   print('shutdown')
   session.pop('logged_in', None) 

def restart_hub():
   os.system("sudo shutdown -r now") 
   print('restart')
   session.pop('logged_in', None)    
   
def loggin_required(f):
   @wraps(f)
   def wrap(*args, **kwargs):
      if 'logged_in' in session:
         return f(*args, **kwargs)
      else:
         flash("You need to login!")
         return redirect(url_for('login'))
   return wrap
   
@app.route("/data", methods=['GET', 'POST'])
@loggin_required
def index():   
   read_zmq()      
   return render_template("index.html", **msg_received)

@app.route('/login', methods=['GET', 'POST'])
def login():   
   session.permanent = True
   error = None
   if request.method == 'POST':
     if request.form['username'] != app_user or request.form['password'] != app_psw:
        error = 'Invalid credentials. Please, try again.'
     else:
        session['logged_in'] = True
        print('Logged in')
        return redirect(url_for('index'))
   return render_template('login.html', error=error)
 
@app.route('/logout', methods=['GET', 'POST'])
@loggin_required
def logout():
   session.pop('logged_in', None)
   flash('Logged out!')
   return redirect(url_for('login'))

@app.route("/restart", methods=['GET','POST'])
@loggin_required
def restart():  
   t = multitimer.MultiTimer(interval=5, function=restart_hub, count=1, runonstart=True)
   t.start()        
   return render_template("restart.html")

@app.route("/shutdown", methods=['GET','POST'])
@loggin_required
def shutdown():         
   t = multitimer.MultiTimer(interval=5, function=shutdown_hub, count=1, runonstart=True)   
   t.start()  
   return render_template("shutdown.html")

@app.route("/wifi", methods=['GET','POST'])
@loggin_required
def wifi():   
   error = None
   wifi_update = None
   if request.method == 'POST':
      if request.form['wifi'] == 'personal':
         if all(request.form[x] != "" for x in ('ssid', 'pwd')):
            ssid = request.form['ssid']
            pwd = request.form['pwd']
            print("\nWifi: {} , ssdi: {} , pwd: {}\n".format(request.form['wifi'],ssid,pwd))
            wpa.configure_wifi_personal(ssid,pwd)
            wifi_update = True
         else:
            error = "Please, fill all fields."
      elif request.form['wifi'] == 'enterprise':
         if all(request.form[x] != "" for x in ('ssid', 'ident', 'pwd')):
            ssid = request.form['ssid']
            pwd = request.form['pwd']      
            ident = request.form['ident']      
            print("\nWifi: {} , ssdi: {} , ident: {} , pwd: {}\n".format(request.form['wifi'],ssid,ident,pwd)) 
            wpa.configure_wifi_enterprise(ssid,ident,pwd)
            wifi_update = True
         else:
            error = "Please, fill all fields."
      if wifi_update == True:
         wifi_update = None
         return render_template("wifi_update.html")
   return render_template("wifi.html",error=error)

@app.route("/waveform", methods=['GET','POST'])
@loggin_required
def waveform():
   return render_template("graph_waveforms.html")

def read_zmq():   
   global msg_received  
   try:
      new_msg = sock_sub.recv_json(zmq.NOBLOCK)
   except Exception:
      pass
   else:   
      msg_received = new_msg
      print("ZMQ data received: ", msg_received)
      
def get_config_file_param(key):
      config_parser = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
      config_parser.read("/home/pi/hub_config.ini")#/home/pi/hub_config.ini
      try:
         v = config_parser['webserver'][key].replace("\"","")
         print("File parameter read -> {} ".format(key))
      except Exception as e:
         print("Error reading configuration file: {}".format(e))
      else:
         return v   
        
if __name__ == "__main__":
   
   app_user = get_config_file_param('user')
   app_psw = get_config_file_param('psw')
   app.secret_key = get_config_file_param('secret_key')
   app.permanent_session_lifetime = timedelta(days=1)
 
   app.run(host='0.0.0.0', port=5000, debug=True)