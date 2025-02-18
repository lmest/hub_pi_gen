#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>
#include "hw.h"
#include "phy.h"
#include "rf_hw.h"
#include "rf_app.h"

static uint32_t max_ack_timeout_ms = 0;
static rf_app_tx_cbk_func __tx_cbk = NULL;
static rf_app_rx_cbk_func __rx_cbk = NULL;
static rf_app_cca_cbk_func __cca_cbk = NULL;
static rf_app_fail_cbk_func __fail_cbk = NULL;

void rf_app_cca_indication(bool channel_is_idle)
{
	if(__cca_cbk)
		__cca_cbk(channel_is_idle);
}

void rf_app_rx_indication(uint8_t *buffer, PHY_Frame_Header_Fields_t frame_header)
{
	if(__rx_cbk)
		__rx_cbk(buffer,frame_header);
}

void rf_app_tx_indication(rf_status_t status)
{
	if(__tx_cbk)
		__tx_cbk(status);
}

void rf_app_critical_fail_indication(rf_error_t fail_code)
{
	if(__fail_cbk)
		__fail_cbk(fail_code);
}

void rf_app_default_config(rf_config_t *config)
{
	config->channel = RF_CHANNEL_2480MHz;
	config->pan_id = 4660;
	config->data_rate = RF_DR_250kbps;
	config->addr = 0;	
	config->tx_power = RF_TXPWR_4dBm;
	config->mode = PHY_DEVICE_MODE;
	config->max_frame_retries = 15;
	config->max_csma_retries = 5;
	config->min_csma_be = 1;
	config->max_csma_be = 4;
	config->cca_mode = CCA_MODE_1;
	config->cca_threshold = RF_CCA_THRESHOLD_94;
	config->ack_time = ACK_2_SYM;
	config->reduced_power_enable = false;
	config->always_return_state_rx = true;
	config->multicast = false;
}

static void rf_app_time_max_timeout_ack_ms(rf_config_t *config)
{
	uint32_t temp_ack_time_us = 0, csma_backoff_time = 0;
	uint8_t currrent_be = 0;
	const uint32_t data_rates[4] = {250000, 500000, 1000000, 2000000};

	//Worst scenario is CSMA/CA fail until last max value, then send frame and wait ack timeout. Then repeat this steps until max frame retries.
	currrent_be = config->min_csma_be;
	for(uint8_t index = 1; index < config->max_csma_retries; index++)			//max_csma_retries - 1 channel fail -> after free channel
	{
		csma_backoff_time = csma_backoff_time + ((1 << currrent_be) - 1);
		currrent_be++;
		if(currrent_be > config->max_csma_be)
			currrent_be = config->max_csma_be;
	}
	temp_ack_time_us = (csma_backoff_time * RF_BACKOFF_PERIOD_US) * (config->max_frame_retries + 1);								//CSMA max duration
	temp_ack_time_us = temp_ack_time_us + (RF_CCA_PERIOD_US * (config->max_csma_retries - 1) * (config->max_frame_retries + 1));	//CCA perform
	temp_ack_time_us = temp_ack_time_us + ((((127)*8*1000000)
					   / data_rates[config->data_rate])  * (config->max_frame_retries + 1));										//TX frame time 127 bytes
	temp_ack_time_us = temp_ack_time_us + (RF_ACK_TIMEOUT_US * (config->max_frame_retries + 1));									//ACK timeout
	max_ack_timeout_ms = ((temp_ack_time_us*CORREC_FACTOR_ACK_TIME)/100) / 1000;
}

uint32_t rf_app_get_max_timeout_ack_ms(void)
{
	return max_ack_timeout_ms;
}


rf_send_status_t rf_app_tx_data(uint8_t *buffer, uint8_t size, uint16_t pan_id_addr, uint16_t dst_addr, bool app_retransmission)
{
	//rf_hw_disable_irq();
	rf_send_status_t status = PHY_DataReq(buffer, size, pan_id_addr, dst_addr, app_retransmission);
	rf_hw_enable_irq();
	printf("| Send Addr = %d | Sequence = %d | size = %hhu | pan_id = %hu\n", dst_addr, PHY_GetNextSeqNumber(true),size,pan_id_addr);
    return status;
}

void rf_app_set_rf_channel(uint8_t channel)
{
	PHY_SetChannel(channel);
}

void rf_app_request_ack(bool ack)
{
	((ack)?(PHY_Enable_ACK()):(PHY_Disable_ACK()));
}

void rf_app_set_state_to_return(PhyReturnState_t state_to_return)
{
	PHY_Set_State_to_Return(state_to_return);
}

void rf_app_wakeup(void)
{
	PHY_Wakeup();
}

void rf_app_sleep(void)
{
	PHY_Sleep();
}

void rf_app_init(rf_config_t *config, rf_app_tx_cbk_func tx_cbk, rf_app_rx_cbk_func rx_cbk, rf_app_cca_cbk_func cca_cbk, rf_app_fail_cbk_func fail_cbk)
{
	PHY_Init(config->mode);

	PHY_Set_Multicast(config->multicast);
	PHY_SetShortAddr(config->addr);
	PHY_SetPanId(config->pan_id);
	PHY_SetChannel(config->channel);
	PHY_SetMaxFrameRetries(config->max_frame_retries);
	PHY_SetMaxCSMARetries(config->max_csma_retries);
	PHY_SetDataRate(config->data_rate);
	PHY_SetCSMABackoff(config->min_csma_be,config->max_csma_be);
	PHY_DisableClockExternalOutput();

	__tx_cbk = tx_cbk;
	__rx_cbk = rx_cbk;
	__cca_cbk = cca_cbk;
	__fail_cbk = fail_cbk;

	switch(config->mode)
	{
	case PHY_PROMISCUOUS_MODE:
	case PHY_SNIFFER_MODE:
		PHY_SetRxState(true,true);
		break;
	case PHY_DEVICE_MODE:
		rf_app_time_max_timeout_ack_ms(config);
		PHY_Set_CCA_Mode(config->cca_mode);
		PHY_Set_CCA_Threshold(config->cca_threshold);
		PHY_SetACKTime(config->ack_time);
		PHY_Enable_ACK();
		PHY_SetReducedPowerMode(config->reduced_power_enable);
		PHY_Set_Init_Mode(config->always_return_state_rx);
		break;
	case PHY_SITE_SURVEY_CCA:
		PHY_Set_CCA_Mode(config->cca_mode);
		PHY_Set_CCA_Threshold(config->cca_threshold);
		PHY_Disable_ACK();
		PHY_SetRxState(true,false);
		PHY_DisableRxPath();
		break;
	default:
		break;
	}

	if(config->pa_enabled)
	{
		// use -2 as max power or pa will be damaged
		PHY_SetPAExtCtrl(true);
		PHY_SetTxPower(RF_TXPWR_m2dBm);
	}
	else
	{
		PHY_SetPAExtCtrl(false);
		PHY_SetTxPower(config->tx_power);
	}
	
}

