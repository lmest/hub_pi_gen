/*
 * rf_app.h
 *
 *  Created on: 5 de set de 2019
 *      Author: marce
 */

#ifndef RF_APP_H_
#define RF_APP_H_

#define RF_SYMBOL_TIME_US			16
#define RF_ACK_TIMEOUT				54 										//54 symbols - pag.64 of Datasheet AT86RF233
#define RF_ACK_TIMEOUT_US			RF_ACK_TIMEOUT*RF_SYMBOL_TIME_US
#define RF_BACKOFF_PERIOD			20 										//20 symbols - pag.159 of IEEE Standard 802.15.4
#define RF_BACKOFF_PERIOD_US		RF_BACKOFF_PERIOD*RF_SYMBOL_TIME_US
#define RF_CCA_PERIOD				8										//8 symbols - pag.66 of IEEE Standard 802.15.4
#define RF_CCA_PERIOD_US			RF_CCA_PERIOD*RF_SYMBOL_TIME_US

#define CORREC_FACTOR_ACK_TIME		80

typedef enum ack_time_e
{
	ACK_12_SYM = 0,
	ACK_2_SYM  = 1,
} ack_time_t;

typedef enum rf_status_e
{
	RF_APP_ERROR = 1,
	RF_APP_OK    = 0,
} rf_status_t;

typedef enum rf_error_e
{
	RF_NO_ERROR 		= 0,
	RF_ERROR_WAIT_STATE = 1,
} rf_error_t;

typedef enum {
	RF_CCA_THRESHOLD_94   			= 0x00,
	RF_CCA_THRESHOLD_92   			= 0x01,
	RF_CCA_THRESHOLD_90   			= 0x02,
	RF_CCA_THRESHOLD_88   			= 0x03,
	RF_CCA_THRESHOLD_86   			= 0x04,
	RF_CCA_THRESHOLD_84   			= 0x05,
	RF_CCA_THRESHOLD_82   			= 0x06,
	RF_CCA_THRESHOLD_80   			= 0x07,
	RF_CCA_THRESHOLD_78   			= 0x08,
	RF_CCA_THRESHOLD_76   			= 0x09,
	RF_CCA_THRESHOLD_74   			= 0x0A,
	RF_CCA_THRESHOLD_72  			= 0x0B,
	RF_CCA_THRESHOLD_70   			= 0x0C,
	RF_CCA_THRESHOLD_68   			= 0x0D,
	RF_CCA_THRESHOLD_66   			= 0x0E,
	RF_CCA_THRESHOLD_64  			= 0x0F
} rf_cca_threshold_t;

typedef enum {
	RF_RX_SENSITIVITY_THRESHOLD_MAX = 0x00,
	RF_RX_SENSITIVITY_THRESHOLD_94  = 0x01,
	RF_RX_SENSITIVITY_THRESHOLD_91  = 0x02,
	RF_RX_SENSITIVITY_THRESHOLD_88  = 0x03,
	RF_RX_SENSITIVITY_THRESHOLD_85  = 0x04,
	RF_RX_SENSITIVITY_THRESHOLD_82  = 0x05,
	RF_RX_SENSITIVITY_THRESHOLD_79  = 0x06,
	RF_RX_SENSITIVITY_THRESHOLD_76  = 0x07,
	RF_RX_SENSITIVITY_THRESHOLD_73  = 0x08,
	RF_RX_SENSITIVITY_THRESHOLD_70  = 0x09,
	RF_RX_SENSITIVITY_THRESHOLD_67  = 0x0A,
	RF_RX_SENSITIVITY_THRESHOLD_64  = 0x0B,
	RF_RX_SENSITIVITY_THRESHOLD_61  = 0x0C,
	RF_RX_SENSITIVITY_THRESHOLD_58  = 0x0D,
	RF_RX_SENSITIVITY_THRESHOLD_55  = 0x0E,
	RF_RX_SENSITIVITY_THRESHOLD_52  = 0x0F
} rf_rx_sensitivity_threshold_t;

typedef enum {
	RF_DR_250kbps 					= 0x00,
	RF_DR_500kbps 					= 0x01,
	RF_DR_1Mbps   					= 0x02,
	RF_DR_2Mbps   					= 0x03,
} rf_data_rate_t;

typedef enum {
	RF_TXPWR_4dBm   				= 0x00,
	RF_TXPWR_3d7dBm 				= 0x01,
	RF_TXPWR_3d4dBm 				= 0x02,
	RF_TXPWR_3dBm   				= 0x03,
	RF_TXPWR_2d5dBm 				= 0x04,
	RF_TXPWR_2dBm   				= 0x05,
	RF_TXPWR_1dBm   				= 0x06,
	RF_TXPWR_0dBm   				= 0x07,
	RF_TXPWR_m1dBm  				= 0x08,
	RF_TXPWR_m2dBm  				= 0x09,
	RF_TXPWR_m3dBm  				= 0x0A,
	RF_TXPWR_m4dBm  				= 0x0B,
	RF_TXPWR_m6dBm  				= 0x0C,
	RF_TXPWR_m8dBm  				= 0x0D,
	RF_TXPWR_m12dBm 				= 0x0E,
	RF_TXPWR_m17dBm 				= 0x0F,
} rf_tx_power_t;

typedef enum {
	RF_CHANNEL_2405MHz  			= 0x0B,
	RF_CHANNEL_2410MHz  			= 0x0C,
	RF_CHANNEL_2415MHz  			= 0x0D,
	RF_CHANNEL_2420MHz  			= 0x0E,
	RF_CHANNEL_2425MHz  			= 0x0F,
	RF_CHANNEL_2430MHz  			= 0x10,
	RF_CHANNEL_2435MHz  			= 0x11,
	RF_CHANNEL_2440MHz 				= 0x12,
	RF_CHANNEL_2445MHz  			= 0x13,
	RF_CHANNEL_2450MHz				= 0x14,
	RF_CHANNEL_2455MHz 				= 0x15,
	RF_CHANNEL_2460MHz  			= 0x16,
	RF_CHANNEL_2465MHz  			= 0x17,
	RF_CHANNEL_2470MHz  			= 0x18,
	RF_CHANNEL_2475MHz				= 0x19,
	RF_CHANNEL_2480MHz  			= 0x1A,
} rf_channel_t;

typedef struct rf_config_s
{
	uint8_t        channel;
	rf_data_rate_t data_rate;
	uint16_t       addr;
	uint16_t       peer_addr;
	uint16_t       pan_id;
	rf_tx_power_t  tx_power;
	PHY_OperationMode_t  mode;
	uint8_t max_frame_retries;
	uint8_t max_csma_retries;
	uint8_t min_csma_be;
	uint8_t max_csma_be;
	PHY_CCA_Mode_t cca_mode;
	rf_cca_threshold_t cca_threshold;
	ack_time_t ack_time;
	bool reduced_power_enable;
	bool always_return_state_rx;
	bool multicast;
} rf_config_t;


typedef void (*rf_app_rx_cbk_func)(uint8_t *buffer, PHY_Frame_Header_Fields_t frame_header);
typedef void (*rf_app_tx_cbk_func)(rf_status_t status);
typedef void (*rf_app_cca_cbk_func)(bool channel_is_idle);
typedef void (*rf_app_fail_cbk_func)(rf_error_t fail_code);

void rf_app_default_config(rf_config_t *config);
uint32_t rf_app_get_max_timeout_ack_ms(void);
rf_send_status_t rf_app_tx_data(uint8_t *buffer, uint8_t size, uint16_t pan_id_addr, uint16_t dst_addr, bool app_retransmission);
void rf_app_set_state_to_return(PhyReturnState_t state_to_return);
void rf_app_wakeup(void);
void rf_app_sleep(void);
void rf_app_init(rf_config_t *config, rf_app_tx_cbk_func tx_cbk, rf_app_rx_cbk_func rx_cbk, rf_app_cca_cbk_func cca_cbk, rf_app_fail_cbk_func fail_cbk);
void rf_app_set_rf_channel(uint8_t channel);
void rf_app_request_ack(bool ack);
void rf_app_rx_indication(uint8_t *buffer, PHY_Frame_Header_Fields_t frame_header);
void rf_app_tx_indication(rf_status_t status);
void rf_app_cca_indication(bool channel_is_idle);
void rf_app_critical_fail_indication(rf_error_t fail_code);

#endif /* RF_APP_H_ */
