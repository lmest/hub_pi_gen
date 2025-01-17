#define PIN_HIGH	1
#define PIN_LOW 	0

#define MILLION 1E6

#define AT86_7_RST_GPIO		13	//verde
#define AT86_9_IRQ_GPIO		6	//amarelo
#define AT86_10_SLPTR_GPIO	5	//marrom
#define AT86_15_SEL_GPIO	25	//laranja

//RPI_LED4_GPIO	18 AZUL //Reservado para indicação de atividade da CPU
#define RPI_LED3_GPIO	12 //verde (indica que o programa do hub esta em operacao)
#define RPI_LED2_GPIO	24 //amarelo (em comunicaacao com sensores)
#define RPI_LED1_GPIO	18 //vermelho (indicação de erros ou falhas)
#define RPI_BTN1_GPIO	26
#define RPI_BTN2_GPIO	21


typedef void (*TimerFunc_t)    (void);

void hw_at86_disable_irq(void);
void hw_at86_enable_irq(void);

void hw_at86_rst_clear(void);
void hw_at86_rst_set(void);

void hw_at86_slp_tr_set(void);
void hw_at86_slp_tr_clear(void);

void hw_at86_reset(void);
void hw_at86_init(void);

void hw_at86_spi_select(void);
void hw_at86_spi_deselect(void);
uint8_t hw_at86_spi_write_byte(uint8_t value);

void hw_at86_reset(void);
void hw_at86_init(void);

uint32_t hw_timer_get_tick_us(void);
uint32_t hw_timer_get_tick_ms(void);
void hw_timer_init_us(void);
void hw_timer_delay_ms(uint32_t delay);
void hw_timer_delay_ns(uint32_t delay_ns);
uint32_t hw_timer_elapsed_ms(uint32_t start);


int rpi_open_spi(int rate);
void rpi_close_spi(void);
void rpi_at86_interrupt(int gpio, int level, uint32_t tick);
//void rpi_led(void);
void rpi_gpio_on(int gpio_id);
void rpi_gpio_off(int gpio_id);
void rpi_led(int led_id);
/*void rpi_fan_off(void);
void rpi_fan_on(void);*/

int hw_set_resistor_pull_up(int gpio);
int hw_set_resistor_pull_down(int gpio);
int hw_set_resistor_pull_off(int gpio);
int hw_set_gpio_input(int gpio);
int hw_set_gpio_output(int gpio);

void rpi_gpio_initiate(void);
void rpi_reset(void);

void hw_set_timer(unsigned timer_id, unsigned millis, TimerFunc_t function_cbk);
void hw_timer_print_dot(void);
void hw_timer_led_msg_recv(void);
void hw_timer_restar_app(void);
int hw_timers_init(void);
void hw_timer_wait_reset(void);
