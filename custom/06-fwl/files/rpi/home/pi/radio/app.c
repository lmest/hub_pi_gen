#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <unistd.h>
#include <pigpio.h>
#include <zmq.h>
#include <string.h>
#include "hw.h"
#include "phy.h"
#include "rf_app.h"
#include "app_cmng.h"
#include "cmng.h"
#include "cbf.h"
#include "ini.h"
#include "app.h"

#define LED_GPIO_ON 1
#define READ_OK 1
#define READ_ERROR 0
#define ZIGBEE_CHANNEL 0
#define ZIGBEE_PAN_ID 1
#define TIMER_SET_OK 0
#define WAIT_TIME_RESET_HOUR 2
#define FINISH_PROGRAM 1

#define MAX_FILE_KEY_SIZE 17
#define MAX_FILE_PARAM 4
#define INVALID_FILE_PARAMETER -1
#define MAX_FILE_LINE_CHAR 128

typedef enum app_reset_reason_e
{
	APP_RESET_NONE = 0,
	APP_RESET_PIGPIO_INIT_ERROR,
	APP_SPI_INIT_ERROR,
	APP_PIGPIO_CFG_ERROR,
	APP_TIMER_INIT_ERROR,
} app_reset_reason_t;

typedef struct hub_configuration_s
{
    uint16_t channel;
    uint16_t pan_id;
    uint16_t radio_wtd;
    uint16_t server_wtd;
} hub_configuration_t;

rf_config_t radio_config;
uint8_t buffer_cmng[MAX_BUFFER_SIZE_MSG];
volatile uint8_t tx_status = 0;
extern uint16_t max_wait_time_reset;
uint8_t end_prog;
extern volatile uint8_t led_msg_recv;
volatile bool rx_data = false;

void app_rasp_restart(app_reset_reason_t reason)
{
	printf("|\n| Hardware Init Fail (reason %d) |\n",(unsigned int) reason);
	printf("|\n| Aborting...\n");
	printf("|***********************************************************************\n\n");
        exit(1);
	//system("sudo shutdown -r now");
}

void app_init_config(rf_config_t *conf)
{
	//conf->channel = RF_CHANNEL_2480MHz;
	//conf->pan_id = 0x1234;
	conf->data_rate = RF_DR_250kbps;
	conf->addr = 0x0B;
	conf->max_frame_retries = 10;
	conf->max_csma_retries = 3;
	conf->ack_time = ACK_2_SYM;
	conf->min_csma_be = 1;
	conf->max_csma_be = 4;
	conf->cca_threshold = RF_CCA_THRESHOLD_84;
	conf->reduced_power_enable = false;		//set this if you want enable Reduced Power Consumption Mode (RPC)
	conf->always_return_state_rx = true; 		//set if you want to be in RX state during all idle radio period
	conf->multicast = true;
}

//Callback for transmission
void app_tx_cbk(rf_status_t status)
{
	tx_status = status; 
}

//Callback for reception
void app_rx_cbk(uint8_t *buffer, PHY_Frame_Header_Fields_t frame_header) //New stack
{
	if(frame_header.dst_addr != 0xFFFF)
	{
		app_cmng_filter_out(buffer, frame_header.size, frame_header.src_addr, frame_header.ed);
		led_msg_recv = LED_GPIO_ON;
		rx_data = true;
	}
}

//New stack
void app_cca_cbk(bool channel_is_idle){}

void app_radio_fail_cbk(rf_error_t fail)
{
	printf("|\n| Radio cbk reset! \n|\n");
	app_radio_restart();
}

void hw_init(void)
{
	gpioTerminate();

	if (gpioInitialise() < 0)
		app_rasp_restart(APP_RESET_PIGPIO_INIT_ERROR);

	if (rpi_open_spi(4000000) < 0)
		app_rasp_restart(APP_SPI_INIT_ERROR);

	if(hw_set_gpio_input(AT86_9_IRQ_GPIO) < 0)
		app_rasp_restart(APP_PIGPIO_CFG_ERROR);

	if (hw_set_resistor_pull_off(AT86_9_IRQ_GPIO) == 0)
		printf("| Pull up resistor for radio interruption set!\n|\n");

	if (gpioSetISRFunc(AT86_9_IRQ_GPIO, FALLING_EDGE, 10, rpi_at86_interrupt) == 0)
		printf("| GPIO change state callback set!\n|\n");

	if (hw_set_gpio_output(RPI_LED3_GPIO) < 0)
		app_rasp_restart(APP_PIGPIO_CFG_ERROR);
	if (hw_set_gpio_output(RPI_LED2_GPIO) < 0)
		app_rasp_restart(APP_PIGPIO_CFG_ERROR);
	if (hw_set_gpio_output(RPI_LED1_GPIO) < 0)
		app_rasp_restart(APP_PIGPIO_CFG_ERROR);

	rpi_gpio_on(RPI_LED3_GPIO);
	rpi_gpio_off(RPI_LED2_GPIO);
	rpi_gpio_off(RPI_LED1_GPIO);
}

static int file_handler(void* user, const char* section, const char* name, const char* value)
{
    hub_configuration_t* pconfig = (hub_configuration_t*)user;
    #define MATCH(s, n) strcmp(section, s) == 0 && strcmp(name, n) == 0

    if (MATCH("radio", "channel")) 
    {
        pconfig->channel = atoi(value);
		radio_config.channel = pconfig->channel;
		printf("| Zigbee Channel: %d\n", radio_config.channel);		
    } 
    else if (MATCH("radio", "pan_id")) 
    {
        pconfig->pan_id = atoi(value);
		radio_config.pan_id = pconfig->pan_id;
		app_cmng_set_pan_id(radio_config.pan_id);
		printf("| Zigbee Pan ID: %d\n", radio_config.pan_id);		
    } 
    else if (MATCH("radio", "radio_wtd_time")) 
    {
        pconfig->radio_wtd = atoi(value);
		printf("| Radio Time Reset: %d minutes\n", pconfig->radio_wtd);
		max_wait_time_reset = pconfig->radio_wtd;
    }     
	   
	return 1;
}

void read_file()
{
	hub_configuration_t config;

	max_wait_time_reset = 180;

	printf("| Reading Init File...\n");

	int error = ini_parse("/home/pi/hub_config.ini", file_handler, &config) ;

    if (error < 0) 
    {
        printf("| Error Openning File!\n");
    }
	else if (error) {
        printf("| Bad config file (first error on line %d)!\n", error);
    }
}

void app_radio_init(void)
{
	end_prog = 0;
    hw_init();

	if(cmng_init() == CMNG_OK)
        printf("| ZMQ set!\n|\n");
    else
	{
		printf("| ZMQ error!\n|\n");
		end_prog = FINISH_PROGRAM;
	}       

    rf_app_default_config(&radio_config); 

	read_file(); 

	if(hw_timers_init() == TIMER_SET_OK)
		printf("| Timers init Ok!\n|\n");
	else
	{
		printf("| Timers init error!\n|\n");
		app_rasp_restart(APP_TIMER_INIT_ERROR);
	}

    app_init_config(&radio_config); 
    rf_app_init(&radio_config, app_tx_cbk, app_rx_cbk, app_cca_cbk, app_radio_fail_cbk); 

	printf("|***********************************************************************\n|\n");
	printf("| Status: RPi initialization finished!\n|\n");
}

void app_radio_restart(void)
{
    rf_app_init(&radio_config, app_tx_cbk, app_rx_cbk, app_cca_cbk, app_radio_fail_cbk); 
}

int main(void)
{ 
    int msg_in_size = 0;

    app_cmng_init();	

	app_radio_init();		

    while (end_prog == 0)
    {
        msg_in_size = cmng_read(buffer_cmng);
        if (msg_in_size != -1) //Mensagem do Python->HUB recebida
        {
            app_cmng_put_in_cbf(buffer_cmng, msg_in_size);
        }

        if(app_cmng_cbf_in_bytes_available() > 0) //Há algo na fila in (Python->HUB)
        {
            app_cmng_filter_in();
        }
	}
        
    gpioTerminate();
    cmng_close();

	return 0;
}
