#define _POSIX_C_SOURCE	199309L

#include "at86_config.h"
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <pigpio.h>
#include "hw.h"
#include "phy.h"

#define LED_ON 1
#define LED_OFF 0
#define NUM_DOTS 5
#define TIMER_OK 0
#define TIMER_ERROR 1
#define MIN_2_HOUR 60
#define PRINT_DOT 0
#define HAL_MAX_DELAY      0xFFFFFFFFU
#define MAX_CMD_LEN 64

volatile uint8_t led_msg_recv = 0;
uint16_t max_wait_time_reset;
volatile uint64_t minutes_restart = 0;
int rpi_handle;
volatile uint8_t status_server = 0;
volatile uint32_t hw_tick_ms = 0;

void hw_at86_disable_irq(void)
{
	//printf("IRQ disabled!\n");
	gpioSetISRFunc(AT86_9_IRQ_GPIO, FALLING_EDGE, 0, NULL);
}
void hw_at86_enable_irq(void)
{
	//printf("IRQ enabled!\n");
	gpioSetISRFunc(AT86_9_IRQ_GPIO, FALLING_EDGE, 0, rpi_at86_interrupt);
}

void hw_at86_rst_clear(void)
{
	gpioWrite(AT86_7_RST_GPIO,PIN_LOW);
}

void hw_at86_rst_set(void)
{
	gpioWrite(AT86_7_RST_GPIO,PIN_HIGH);
}

void hw_at86_spi_select(void)
{
	gpioWrite(AT86_15_SEL_GPIO,PIN_LOW);
}

void hw_at86_spi_deselect(void)
{
	gpioWrite(AT86_15_SEL_GPIO,PIN_HIGH);
	for(int i=0 ; i<150 ; i++)
	{

	}
}

void hw_at86_slp_tr_set(void)
{
	gpioWrite(AT86_10_SLPTR_GPIO,PIN_HIGH);
}

void hw_at86_slp_tr_clear(void)
{
	gpioWrite(AT86_10_SLPTR_GPIO,PIN_LOW);
}

uint8_t hw_at86_spi_write_byte(uint8_t tx_data)
{
	uint8_t rx_data;

	if(spiXfer(rpi_handle,(char*)(&tx_data),(char*)(&rx_data),1) >= 0)
		return rx_data;

	else
		return 0;
}

void hw_at86_reset(void)
{
	hw_at86_rst_clear();
	hw_timer_delay_ms(2);
	hw_at86_rst_set();
}

void hw_at86_init(void)
{
	hw_at86_slp_tr_clear();
}


void hw_timer_delay_ms(uint32_t delay_ms)
{
	  struct timespec t_ms = {0, delay_ms*1000000L};
	  nanosleep(&t_ms,NULL);
}

void hw_timer_delay_ns(uint32_t delay_ns)
{
	  struct timespec t_ns = {0, delay_ns};
	  nanosleep(&t_ns,NULL);
}

int hw_set_resistor_pull_up(int gpio)
{
	int value;
	value = gpioSetPullUpDown(gpio,PI_PUD_UP);
	return value;
}

int hw_set_resistor_pull_down(int gpio)
{
	int value;
	value = gpioSetPullUpDown(gpio,PI_PUD_DOWN);
	return value;
}

int hw_set_resistor_pull_off(int gpio)
{
	int value;
	value = gpioSetPullUpDown(gpio,PI_PUD_OFF);
	return value;
}

int hw_set_gpio_input(int gpio)
{
	int value;
	value = gpioSetMode(gpio,PI_INPUT);
	return value;
}

int hw_set_gpio_output(int gpio)
{
	int value;
	value = gpioSetMode(gpio,PI_OUTPUT);
	return value;
}


int rpi_open_spi(int rate)
{	
	rpi_handle = spiOpen(0,rate,0);//256000,0);
	if (rpi_handle >= 0)
	{
		printf("| Status: SPI open succesfully!\n|\n");
	}
	
	return rpi_handle;
}

void rpi_close_spi(void)
{
	spiClose(rpi_handle);
}

void rpi_at86_interrupt(int gpio, int level, uint32_t tick)
{
	PHY_TaskHandler();	
}

void rpi_gpio_on(int gpio_id)
{
	gpioWrite(gpio_id,PIN_HIGH);
}

void rpi_gpio_off(int gpio_id)
{
	gpioWrite(gpio_id,PIN_LOW);
}

void rpi_led_toggle(int led_id)
{
	int aux_rpi_led = gpioRead(led_id);
	if(aux_rpi_led == 0)
		rpi_gpio_on(led_id);
	else
		rpi_gpio_off(led_id);
}

void rpi_reset(void)
{
	gpioTerminate();
	gpioInitialise();
}

void hw_set_timer(unsigned timer_id, unsigned millis, TimerFunc_t function_cbk)
{
	gpioSetTimerFunc(timer_id, millis, function_cbk);
}

void hw_timer_print_dot(void)
{
	static uint8_t dot_num = 0;

	if(dot_num < NUM_DOTS)
	{
		printf(".");
		fflush(stdout);
		dot_num++;
	}		
	else 
	{
		printf("\33[2K\r");
		dot_num = 0;
	}
}

void hw_timer_led_msg_recv(void)
{
	if(led_msg_recv == LED_ON)
	{
		rpi_gpio_on(RPI_LED2_GPIO);
		led_msg_recv = LED_OFF;
	}
	else if(led_msg_recv == LED_OFF)
	{
		rpi_gpio_off(RPI_LED2_GPIO);
	}

	if(status_server == 0)
	{
		rpi_led_toggle(RPI_LED3_GPIO);
	}
}

void hw_timer_restar_app(void)
{
	minutes_restart++;

	if (minutes_restart >= max_wait_time_reset)
	{
		// This mechanism is not used anymore as it has a side effect where hubs starts to restart
		// when we do not have any sensor near it. The python code will handle resets due to 
		// communication failure.

		#if 0
		rpi_gpio_on(RPI_LED1_GPIO);
		rpi_gpio_off(RPI_LED2_GPIO);
		rpi_gpio_off(RPI_LED3_GPIO);

		printf("|\n| Communication Error: Hub shutting down raspberry...\n");
		printf("|***********************************************************************\n\n");
		system("sudo shutdown -r now");
		#endif
	}
}

void hw_timer_tick_ms(void)
{
	hw_tick_ms+=10;
}

uint32_t hw_timer_elapsed_ms(uint32_t start)
{
	uint32_t elapsed;
	uint32_t now = hw_timer_get_tick_ms();

	if(now < start)
		elapsed = (HAL_MAX_DELAY - start) + now + 1;
	else
		elapsed = now - start;

	return elapsed;
}

uint32_t hw_timer_get_tick_ms(void)
{
	return hw_tick_ms;
}

int hw_timers_init(void)
{
	int return_value = TIMER_OK;

#if PRINT_DOT ==  1
	if(gpioSetTimerFunc(0, 5000, hw_timer_print_dot) != TIMER_OK)
		return_value =  TIMER_ERROR;
#endif

	if(gpioSetTimerFunc(1, 1000, hw_timer_led_msg_recv) != TIMER_OK)
		return_value =  TIMER_ERROR;

	if(gpioSetTimerFunc(2, 60000, hw_timer_restar_app) != TIMER_OK)
		return_value =  TIMER_ERROR;

	if(gpioSetTimerFunc(3, 10, hw_timer_tick_ms) != TIMER_OK)
		return_value =  TIMER_ERROR;	

	return 	return_value;
}

void hw_timer_wait_reset(void)
{
	minutes_restart = 0;
}

