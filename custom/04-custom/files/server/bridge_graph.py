import plotly.graph_objects as go
import configparser
from logging_conf import *

dir = "/home/pi/webserver/templates/"
is_bridge_enabled = 0
bypass_server_req = 0

def save_three_graphs_html(vib_x_data, vib_z_data, aud_data, sid, temp, bat, time):
    # Create a subplot with 3 rows and 1 column
    fig = go.Figure()
    
    # Add scatter plots to the subplot
    fig.add_trace(go.Scatter(x=list(range(len(vib_x_data))), y=vib_x_data, name="Vibration X"))
    fig.add_trace(go.Scatter(x=list(range(len(vib_z_data))), y=vib_z_data, name="Vibration Z"))
    fig.add_trace(go.Scatter(x=list(range(len(aud_data))), y=aud_data, name="Audio"))  
   
    # Fomat the subplot
    fig.update_layout(
        font_family="Courier New",
        font_color="black",
        title="SENSOR WAVEFORM DATA <br><sup>Sensor ID: {} | Temperature: {} | Battery:  {} | Time: {}</sup>".format(sid, temp/1000, bat/10000, time),
        title_x=0.5,
        title_font_family="Times New Roman",
        title_font_color="black",
        title_font_size=30,
        xaxis_title="Samples",
        yaxis_title="Amplitude",
        legend_title="Select Data",
        )
   
    # Save the subplot as an HTML file
    fig.write_html(dir + "graph_waveforms.html")

def save_graph_html(data, graph_title, file_name):
    # Create a scatter plot
    fig = go.Figure(data=go.Scatter(x=list(range(len(data))), y=data))
    
    # Add title and xaxis/yaxis labels
    fig.update_layout(title=graph_title, 
                      title_x=0.5,
                      xaxis_title='Samples', 
                      yaxis_title='Amplitude',
                      font_family="Times New Roman",
                      font_color="black",
                      title_font_family="Times New Roman",
                      title_font_color="black",
                      title_font_size=40,
        )

    # Save the plot as an HTML file
    fig.write_html(dir + file_name)  
    
def save_graph_img(year, month, day, hour, minute, second, vib_x_data, vib_z_data, aud_data, sid, temp, bat):  
    if(is_bridge_enabled == 1):
        time = "{}-{}-{} {}:{}:{}".format(year, month, day, hour, minute, second)
        save_three_graphs_html(vib_x_data, vib_z_data, aud_data, sid, temp, bat, time)
    else:
        logging.info("Bridge plot is disabled - To enable it, change the value of [bridge] enable to 1 in the configuration file")
    
def bridge_init():
    global is_bridge_enabled
    global bypass_server_req
    
    config = configparser.ConfigParser()
    config.read("/home/pi/hub_config.ini")
    try:
        is_bridge_enabled = int(config['bridge']['enable'])
        if(is_bridge_enabled == 1):
            logging.info("Reading configuration file:  Bridge plot is enabled")
        else:
            logging.info("Reading configuration file:  Bridge plot is disabled")
            
        bypass_server_req = int(config['bridge']['bypass_server_request'])    
        if(bypass_server_req == 1):
            logging.info("Reading configuration file:  Bypass server request is enabled")
        else:
            logging.info("Reading configuration file:  Bypass server request is disabled")
            
    except Exception:
        logging.warning("Error reading configuration file")
        is_bridge_enabled = 0
        bypass_server_req = 0