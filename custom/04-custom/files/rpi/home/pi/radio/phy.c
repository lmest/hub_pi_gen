/**
 * \file phy.c
 *
 * \brief AT86RF233 PHY implementation
 *
 * Copyright (C) 2012-2014, Atmel Corporation. All rights reserved.
 *
 * \asf_license_start
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * 3. The name of Atmel may not be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * 4. This software may only be redistributed and used in connection with an
 *    Atmel microcontroller product.
 *
 * THIS SOFTWARE IS PROVIDED BY ATMEL "AS IS" AND ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT ARE
 * EXPRESSLY AND SPECIFICALLY DISCLAIMED. IN NO EVENT SHALL ATMEL BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *
 * \asf_license_stop
 *
 * Modification and other use of this code is subject to Atmel's Limited
 * License Agreement (license.txt).
 *
 * $Id: phy.c 9267 2014-03-18 21:46:19Z ataradov $
 *
 */

/*- Includes ---------------------------------------------------------------*/
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include "phy.h"
#include "at86rf233.h"
#include "rf_app.h"
#include "rf_hw.h"

/*- Types ------------------------------------------------------------------*/
typedef enum
{
  PHY_STATE_INITIAL = 0,
  PHY_STATE_IDLE,
  PHY_STATE_DEEPSLEEP,
  PHY_STATE_SLEEP,
  PHY_STATE_TX_WAIT_END,
  PHY_STATE_RX,
} PhyState_t;

/*- Prototypes -------------------------------------------------------------*/
static void phyWriteRegister(uint8_t reg, uint8_t value);
static uint8_t phyReadRegister(uint8_t reg);
static bool phyWaitState(uint8_t state);
//static void phyTrxSetState(uint8_t state);
static void phySetRxState(bool auto_ack_retr);

/*- Variables --------------------------------------------------------------*/
volatile PhyState_t phyState = PHY_STATE_INITIAL;
static PHY_Frame_Header_Fields_t rx_frame_header;
static uint8_t phyRxBuffer[128];
volatile bool phyRxState;
static bool req_ack;
volatile bool phy_multicast;
volatile uint8_t phy_seq_num_tx = 0;
volatile uint8_t phy_seq_num_rx = 0xFF;
volatile uint16_t phy_pan_id;
volatile uint16_t phy_addr;
volatile PHY_OperationMode_t phy_mode;
volatile bool always_rx_return_state;
volatile PhyReturnState_t return_state = PHY_RETURN_STATE_RX;
const uint8_t trx_cmd_return_state[3] = {TRX_CMD_TRX_OFF, TRX_CMD_TX_ARET_ON, TRX_CMD_RX_AACK_ON};

/*- Implementations --------------------------------------------------------*/

/*************************************************************************//**
*****************************************************************************/
void PHY_Init(PHY_OperationMode_t mode)
{
  phyState = PHY_STATE_INITIAL;
  phy_seq_num_tx = 0;
  phy_seq_num_rx = 0xFF;
  phy_pan_id = 0;
  phy_addr = 0;
  phy_mode = mode;

  rf_hw_slp_tr_clear();
  rf_hw_reset();
  phyRxState = false;

	phyWriteRegister(TRX_STATE_REG, TRX_CMD_TRX_OFF);
	if(phyWaitState(TRX_STATUS_TRX_OFF) == false)
		rf_app_critical_fail_indication(RF_ERROR_WAIT_STATE);

  switch(phy_mode)
  {
  case PHY_PROMISCUOUS_MODE:
	for(uint8_t n = SHORT_ADDR_0_REG ; n <= IEEE_ADDR_7_REG ; n++)
	  phyWriteRegister(n,0);
  // break missing, intentional
  case PHY_SNIFFER_MODE:
	phyWriteRegister(TRX_CTRL_1_REG, (3<<SPI_CMD_MODE) | (0<<IRQ_MASK_MODE) | (1 << IRQ_POLARITY));
	phyWriteRegister(XAH_CTRL_1_REG, (1 << AACK_PROM_MODE));
	phyWriteRegister(CSMA_SEED_1_REG, (1 << AACK_DIS_ACK));
	break;
  case PHY_SITE_SURVEY_CCA:
  case PHY_DEVICE_MODE:
  default:
	  phyWriteRegister(TRX_CTRL_1_REG, (1<<TX_AUTO_CRC_ON) | (3<<SPI_CMD_MODE) | (0<<IRQ_MASK_MODE) | (1 << IRQ_POLARITY));
	  phyWriteRegister(TRX_CTRL_2_REG, (1<<RX_SAFE_MODE) | (1<<OQPSK_SCRAM_EN));
	  break;
  }

  // interrupt handling, per mode
  switch(phy_mode)
  {
  case PHY_PROMISCUOUS_MODE:
  case PHY_SNIFFER_MODE:
  case PHY_DEVICE_MODE:
	  phyWriteRegister(IRQ_MASK_REG,(1 << TRX_END));// | (1 << RX_START));
	  break;
  case PHY_SITE_SURVEY_CCA:
	  phyWriteRegister(IRQ_MASK_REG, (1 << CCA_ED_DONE));
	  break;
  default:
	  break;
  }

  phyReadRegister(IRQ_STATUS_REG);         // irq cleanup

  phyState = PHY_STATE_IDLE;
}

//static uint8_t PHY_GetNextSeqNumber(bool app_retx)
uint8_t PHY_GetNextSeqNumber(bool app_retx)
{
    if(!app_retx)
    {
	if(phy_seq_num_tx < 0xFE)
	    phy_seq_num_tx++;
	
	else
	    phy_seq_num_tx = 0;
    }
    
    return phy_seq_num_tx;
}

/*************************************************************************//**
*****************************************************************************/
void PHY_SetReducedPowerMode(bool enable_reduced_power)
{
	if(enable_reduced_power == true)
	{
		uint8_t msk = 0;
		phyTrxSetState(TRX_CMD_TRX_OFF);
		phyWriteRegister(TRX_RPC_REG, 0xEF); //ENABLE ALL (RX_RPC_CTRL-RX_RPC_EN-PDT_RPC_EN-PLL_RPC_EN-XAH_TX_RPC_EN-IPAN_RPC_EN)
		msk = phyReadRegister(TRX_CTRL_2_REG) & 0x7F;
		phyWriteRegister(TRX_CTRL_2_REG, msk | (1 << RX_SAFE_MODE));
	}
}
/*************************************************************************//**
*****************************************************************************/
void PHY_SetRxState(bool rx, bool auto_ack_retr)
{
  phyRxState = rx;
  phySetRxState(auto_ack_retr);
}
/*************************************************************************//**
*****************************************************************************/
void PHY_SetDIGExternal(void)
{
  uint8_t reg;

  reg = phyReadRegister(TRX_CTRL_1_REG) & 0x3f;
  phyWriteRegister(TRX_CTRL_1_REG, reg | 1 << PA_EXT_EN | 1 << IRQ_2_EXT_EN);
}
/*************************************************************************//**
*****************************************************************************/
void PHY_DisableClockExternalOutput(void)
{
  uint8_t reg;

  reg = phyReadRegister(TRX_CTRL_0_REG) & 0xf0;
  phyWriteRegister(TRX_CTRL_0_REG, reg | 0 << CLKM_SHA_SEL | CLKM_NONE << CLKM_CTRL);
}
/*************************************************************************//**
*****************************************************************************/
void PHY_EnableClockExternalOutput(PHY_External_Clock_t clk_freq)
{
  uint8_t reg;

  reg = phyReadRegister(TRX_CTRL_0_REG) & 0xf0;
  phyWriteRegister(TRX_CTRL_0_REG, reg |  0 << CLKM_SHA_SEL | clk_freq << CLKM_CTRL);
}
void PHY_SetChannel(uint8_t channel)
{
  uint8_t reg;

  reg = phyReadRegister(PHY_CC_CCA_REG) & ~0x1f;
  phyWriteRegister(PHY_CC_CCA_REG, reg | channel);
}

uint8_t PHY_GetChannel(void)
{
  return phyReadRegister(PHY_CC_CCA_REG) & 0x1f;
}

/*************************************************************************//**
*****************************************************************************/
void PHY_SetPanId(uint16_t panId)
{
  uint8_t *d = (uint8_t *)&panId;

  phy_pan_id = panId;

  phyWriteRegister(PAN_ID_0_REG, d[0]);
  phyWriteRegister(PAN_ID_1_REG, d[1]);
}

uint16_t PHY_GetPanId(void)
{
  return ((phyReadRegister(PAN_ID_1_REG) << 8) | phyReadRegister(PAN_ID_0_REG));
}

/*************************************************************************//**
*****************************************************************************/
void PHY_SetShortAddr(uint16_t addr)
{
  uint8_t *d = (uint8_t *)&addr;

  phy_addr = addr;

  phyTrxSetState(TRX_CMD_TRX_OFF);

  phyWriteRegister(SHORT_ADDR_0_REG, d[0]);
  phyWriteRegister(SHORT_ADDR_1_REG, d[1]);
  phyWriteRegister(CSMA_SEED_0_REG, d[0] + d[1]);
}

uint16_t PHY_GetShortAddr(void)
{
  return ((phyReadRegister(SHORT_ADDR_1_REG) << 8) | phyReadRegister(SHORT_ADDR_0_REG));
}

/*************************************************************************//**
*****************************************************************************/
void PHY_SetTxPower(uint8_t txPower)
{
  uint8_t reg;

  reg = phyReadRegister(PHY_TX_PWR_REG) & ~0x0f;
  phyWriteRegister(PHY_TX_PWR_REG, reg | txPower);
}

/*************************************************************************//**
*****************************************************************************/
void PHY_Set_Rx_Sensitivity_Threshold(uint8_t threshold)	//0 to 15.
{
	uint8_t reg;
	reg = phyReadRegister(RX_SYN_REG) & 0xF0;
	phyWriteRegister(RX_SYN_REG, reg | (threshold << RX_PDT_LEVEL));
}

/*************************************************************************//**
*****************************************************************************/
uint8_t PHY_GetTxPower(void)
{
  return phyReadRegister(PHY_TX_PWR_REG) & 0x0f;
}

/*************************************************************************//**
*****************************************************************************/
void PHY_Set_CCA_Mode(PHY_CCA_Mode_t cca_mode)
{
  uint8_t reg;

  reg = phyReadRegister(PHY_CC_CCA_REG) & 0x9f;
  phyWriteRegister(PHY_CC_CCA_REG, reg | (cca_mode << CCA_MODE));
}

/*************************************************************************//**
*****************************************************************************/
void PHY_Set_CCA_Threshold(uint8_t threshold)	//0 to 15.
{
  phyWriteRegister(CCA_THRES_REG, threshold);
}

/*************************************************************************//**
*****************************************************************************/
uint8_t PHY_Get_CCA_Threshold(void)
{
  return phyReadRegister(CCA_THRES_REG) & 0x0f;
}

/*************************************************************************//**
*****************************************************************************/
void PHY_Set_CCA_Request(void)
{
  uint8_t reg;

  reg = phyReadRegister(PHY_CC_CCA_REG);
  phyWriteRegister(PHY_CC_CCA_REG, reg | 0x80);
}

/*************************************************************************//**
*****************************************************************************/
void PHY_DisableRxPath(void)
{
  uint8_t reg;

  reg = phyReadRegister(RX_SYN_REG);
  phyWriteRegister(RX_SYN_REG, reg | 0x80);
}

void PHY_EnableRxPath(void)
{
  uint8_t reg;

  reg = phyReadRegister(RX_SYN_REG);
  phyWriteRegister(RX_SYN_REG, reg  & 0x7f);
}
/*************************************************************************//**
*****************************************************************************/

void PHY_SetCSMABackoff(uint8_t min_be,uint8_t max_be)
{
    phyWriteRegister(CSMA_BE_REG,(max_be << 4) | (min_be & 0x0f));
}

void PHY_GetCSMABackoff(uint8_t *min_be,uint8_t *max_be)
{
    uint8_t val = phyReadRegister(CSMA_BE_REG);
    *min_be = val & 0x0f;
    *max_be = val >> 4;
}

/*************************************************************************//**
*****************************************************************************/
void PHY_SetMaxFrameRetries(uint8_t max_ret)
{
  uint8_t reg;

  reg = phyReadRegister(XAH_CTRL_0_REG) & 0xf;
  phyWriteRegister(XAH_CTRL_0_REG, reg | (max_ret << MAX_FRAME_RETRES));
}

/*************************************************************************//**
*****************************************************************************/
void PHY_SetMaxCSMARetries(uint8_t max_ret)
{
  uint8_t reg;

  reg = phyReadRegister(XAH_CTRL_0_REG) & 0xf1;
  phyWriteRegister(XAH_CTRL_0_REG, reg | (max_ret << MAX_CSMA_RETRES));
}

/*************************************************************************//**
*****************************************************************************/
uint8_t PHY_GetFrameRetries(void)
{
	return (phyReadRegister(XAH_CTRL_2_REG) & 0xf0) >> ARET_FRAME_RETRIES;
}

/*************************************************************************//**
*****************************************************************************/
uint8_t PHY_GetCSMARetries(void)
{
	return (phyReadRegister(XAH_CTRL_2_REG) & 0xf) >> ARET_CSMA_RETRIES;
}

/*************************************************************************//**
*****************************************************************************/
void PHY_SetACKTime(bool ack_time)	//(0) - 12 symbol period /(1) - 2 symbol period
{
  uint8_t reg;
  reg = phyReadRegister(XAH_CTRL_1_REG) & 0xfb;
  phyWriteRegister(XAH_CTRL_1_REG, reg | (ack_time << AACK_ACK_TIME));
}

/*************************************************************************//**
*****************************************************************************/
void PHY_Enable_ACK(void)
{
	req_ack = true;
}

/*************************************************************************//**
*****************************************************************************/
void PHY_Disable_ACK(void)
{
	req_ack = false;
}

/*************************************************************************//**
*****************************************************************************/
void PHY_Set_Multicast(bool multicast)
{
	phy_multicast = multicast;
}

/*************************************************************************//**
*****************************************************************************/
void PHY_Set_Init_Mode(bool rx_state_return)
{
	if(rx_state_return == true)
	{
		always_rx_return_state = true;
		PHY_SetRxState(true,true);
	}
	else
	{
		always_rx_return_state = false;
		phyTrxSetState(trx_cmd_return_state[PHY_RETURN_STATE_TRX_OFF]);
	}
}

/*************************************************************************//**
*****************************************************************************/
void PHY_Set_State_to_Return(PhyReturnState_t state_to_return)
{
	return_state = state_to_return;
}
/*************************************************************************//**
*****************************************************************************/
void PHY_Sleep(void)
{
  phyTrxSetState(TRX_CMD_TRX_OFF);
  rf_hw_slp_tr_set();
  phyState = PHY_STATE_SLEEP;
}

/*************************************************************************//**
*****************************************************************************/
void PHY_DeepSleep(void)
{
  phyTrxSetState(TRX_CMD_TRX_OFF);
  phyTrxSetState(TRX_CMD_PREP_DEEP_SLEEP);
  rf_hw_slp_tr_set();
  phyState = PHY_STATE_DEEPSLEEP;
}

/*************************************************************************//**
*****************************************************************************/
void PHY_Wakeup(void)
{
  rf_hw_slp_tr_clear();

  if(always_rx_return_state == true)
	  phySetRxState(true);
  else
	  phyTrxSetState(trx_cmd_return_state[return_state]);

  phyState = PHY_STATE_IDLE;
}

/*************************************************************************//**
*****************************************************************************/
rf_send_status_t PHY_DataReq(uint8_t *data, uint8_t size, uint16_t pan_id_addr, uint16_t dst_addr, bool app_retx)
{
	if(phyState != PHY_STATE_IDLE)
		return RF_APP_SEND_RADIO_BUSY;

	if(phyTrxSetState(TRX_CMD_TX_ARET_ON) == false)
		return RF_APP_SEND_FAIL_RADIO;

	phyReadRegister(IRQ_STATUS_REG);

	rf_hw_spi_select();
	// data is only the payload, no header is required
	// all frames are sent as data type with compressed pan ID
	rf_hw_write_byte_spi(RF_CMD_FRAME_W);
	rf_hw_write_byte_spi(size + PHY_CRC_SIZE + PHY_HDR_COMP_PAN_ID_SIZE);
	((req_ack)?(rf_hw_write_byte_spi(0x61)):(rf_hw_write_byte_spi(0x41)));
	rf_hw_write_byte_spi(0x88); // short addresses
	rf_hw_write_byte_spi(PHY_GetNextSeqNumber(app_retx));
	rf_hw_write_byte_spi(pan_id_addr & 0xFF);
	rf_hw_write_byte_spi((pan_id_addr >> 8) & 0xFF);
	rf_hw_write_byte_spi(dst_addr & 0xFF);
	rf_hw_write_byte_spi((dst_addr >> 8) & 0xFF);
	rf_hw_write_byte_spi(phy_addr & 0xFF);
	rf_hw_write_byte_spi((phy_addr >> 8) & 0xFF);

	for (uint8_t i = 0; i < size; i++)
		rf_hw_write_byte_spi(data[i]);

	rf_hw_spi_deselect();

	phyState = PHY_STATE_TX_WAIT_END;
	rf_hw_slp_tr_set();
	rf_hw_slp_tr_clear();

	return RF_APP_SEND_OK;
}

uint8_t PHY_ReadChipID(void)
{
	return phyReadRegister(VERSION_NUM_REG);
}

uint8_t PHY_ReadDataRate(void)
{
	return phyReadRegister(TRX_CTRL_2_REG) & 0x07;
}

void PHY_SetDataRate(uint8_t data_rate)
{
	uint8_t msk = phyReadRegister(TRX_CTRL_2_REG) & 0xF8;
	phyWriteRegister(TRX_CTRL_2_REG,msk|data_rate);

  // Header sensibility rx and payload sensibility rx may be different !
  // So we are making both equal for forcing same sensibility levels for header and payload.
  uint8_t rx_sens_th[] = { RF_RX_SENSITIVITY_THRESHOLD_MAX, 
                           RF_RX_SENSITIVITY_THRESHOLD_MAX,
                           RF_RX_SENSITIVITY_THRESHOLD_94,
                           RF_RX_SENSITIVITY_THRESHOLD_88 };

  PHY_Set_Rx_Sensitivity_Threshold(rx_sens_th[data_rate]);
}

uint8_t PHY_GetDataRate(void)
{
	return phyReadRegister(TRX_CTRL_2_REG) & 0x07;
}

uint8_t PHY_GetRSSI(void)
{
	return phyReadRegister(PHY_RSSI_REG) & 0x1F;
}

uint8_t PHY_GetEDLevel(void)
{
	return phyReadRegister(PHY_ED_LEVEL_REG);
}


uint8_t PHY_GetFCSStatus(void)
{
	return phyReadRegister(PHY_RSSI_REG) >> 7;
}
#ifdef PHY_ENABLE_RANDOM_NUMBER_GENERATOR
/*************************************************************************//**
*****************************************************************************/
uint16_t PHY_RandomReq(void)
{
  uint16_t rnd = 0;
  uint8_t rndValue;

  phyTrxSetState(TRX_CMD_RX_ON);

  for (uint8_t i = 0; i < 16; i += 2)
  {
    HAL_Delay(RANDOM_NUMBER_UPDATE_INTERVAL);
    rndValue = (phyReadRegister(PHY_RSSI_REG) >> RND_VALUE) & 3;
    rnd |= rndValue << i;
  }

  phySetRxState();

  return rnd;
}
#endif

#ifdef PHY_ENABLE_AES_MODULE
/*************************************************************************//**
*****************************************************************************/
void PHY_EncryptReq(uint8_t *text, uint8_t *key)
{
  rf_hw_spi_select();
  rf_hw_write_byte_spi(RF_CMD_SRAM_W);
  rf_hw_write_byte_spi(AES_CTRL_REG);
  rf_hw_write_byte_spi((1<<AES_CTRL_MODE) | (0<<AES_CTRL_DIR));
  for (uint8_t i = 0; i < AES_BLOCK_SIZE; i++)
    rf_hw_write_byte_spi(key[i]);
  rf_hw_spi_deselect();

  rf_hw_spi_select();
  rf_hw_write_byte_spi(RF_CMD_SRAM_W);
  rf_hw_write_byte_spi(AES_CTRL_REG);
  rf_hw_write_byte_spi((0<<AES_CTRL_MODE) | (0<<AES_CTRL_DIR));
  for (uint8_t i = 0; i < AES_BLOCK_SIZE; i++)
    rf_hw_write_byte_spi(text[i]);
  rf_hw_write_byte_spi((1<<AES_CTRL_REQUEST) | (0<<AES_CTRL_MODE) | (0<<AES_CTRL_DIR));
  rf_hw_spi_deselect();

  HAL_Delay(AES_CORE_CYCLE_TIME);

  rf_hw_spi_select();
  rf_hw_write_byte_spi(RF_CMD_SRAM_R);
  rf_hw_write_byte_spi(AES_STATE_REG);
  for (uint8_t i = 0; i < AES_BLOCK_SIZE; i++)
    text[i] = rf_hw_write_byte_spi(0);
  rf_hw_spi_deselect();
}
#endif

#ifdef PHY_ENABLE_ENERGY_DETECTION
/*************************************************************************//**
*****************************************************************************/
int8_t PHY_EdReq(void)
{
  uint8_t ed;

  phyTrxSetState(TRX_CMD_RX_ON);
  phyWriteRegister(PHY_ED_LEVEL_REG, 0);

  while (0 == (phyReadRegister(IRQ_STATUS_REG) & (1<<CCA_ED_DONE)));

  ed = (int8_t)phyReadRegister(PHY_ED_LEVEL_REG);

  phySetRxState();

  return ed + PHY_RSSI_BASE_VAL;
}
#endif

/*************************************************************************//**
*****************************************************************************/
static void phyWriteRegister(uint8_t reg, uint8_t value)
{
  rf_hw_spi_select();
  rf_hw_write_byte_spi(RF_CMD_REG_W | reg);
  rf_hw_write_byte_spi(value);
  rf_hw_spi_deselect();
}

/*************************************************************************//**
*****************************************************************************/
static uint8_t phyReadRegister(uint8_t reg)
{
  uint8_t value;

  rf_hw_spi_select();
  rf_hw_write_byte_spi(RF_CMD_REG_R | reg);
  value = rf_hw_write_byte_spi(0);
  rf_hw_spi_deselect();

  return value;
}

uint8_t PHY_ReadIRQStatus(void)
{
	return phyReadRegister(IRQ_STATUS_REG);
}
/*************************************************************************//**
*****************************************************************************/
static bool phyWaitState(uint8_t state)
{
  //while (state != (phyReadRegister(TRX_STATUS_REG) & TRX_STATUS_MASK))
  //  printf("phyWaitState\n");
    
    for(uint16_t i = 0; i <= PHY_MAX_CYCLES_TO_WAIT_RADIO_STATE; i++)
    {
	if(state == (phyReadRegister(TRX_STATUS_REG) & TRX_STATUS_MASK))
	{
	    return true;
	}
    }
    return false;
}

/*************************************************************************//**
*****************************************************************************/
static void phySetRxState(bool auto_ack_retr)
{
  phyTrxSetState(TRX_CMD_TRX_OFF);

  phyReadRegister(IRQ_STATUS_REG);

  if(phyRxState)
  {
    if(auto_ack_retr)
    	phyTrxSetState(TRX_CMD_RX_AACK_ON);
    else
    	phyTrxSetState(TRX_CMD_RX_ON);
  }
}

/*************************************************************************//**
*****************************************************************************/
bool phyTrxSetState(uint8_t state)
{
	uint8_t actual_state = 0;

	actual_state = (phyReadRegister(TRX_STATUS_REG) & TRX_STATUS_MASK);
	if(actual_state == state)
		return true;
	else if(actual_state == TRX_STATUS_STATE_TRANSITION) //"Do not try to initiate a further state change while the radio transceiver is in STATE_TRANSITION_IN_PROGRESS state."
		goto state_radio_fail_handler;

	phyWriteRegister(TRX_STATE_REG, TRX_CMD_FORCE_TRX_OFF);
	if(phyWaitState(TRX_STATUS_TRX_OFF) == false)
		goto state_radio_fail_handler;

	phyWriteRegister(TRX_STATE_REG, state);
	if(phyWaitState(state) == false)
		goto state_radio_fail_handler;

	return true;

state_radio_fail_handler:
	rf_app_critical_fail_indication(RF_ERROR_WAIT_STATE);
	return false;
}

/*************************************************************************//**
*****************************************************************************/
void PHY_TaskHandler(void)
{
  uint8_t status;

  if (PHY_STATE_SLEEP == phyState || PHY_STATE_INITIAL == phyState)
    return;

  status = phyReadRegister(IRQ_STATUS_REG);
/*
  if((phy_mode == PHY_SITE_SURVEY_CCA) && (status & (1 << CCA_ED_DONE)))
  {
	  bool channel_is_idle = phyReadRegister(TRX_STATUS_REG) & (1 << CCA_STATUS);
	  rf_app_cca_indication(channel_is_idle);
  }
  else if(status & (1 << RX_START))
  {
	  phyState = PHY_STATE_RX;
  }
  else if (status & (1<<TRX_END))
  {
    if(PHY_STATE_RX == phyState)
    {*/
    if (status & (1<<TRX_END))
    {
      if(PHY_STATE_IDLE == phyState)
      {
		uint8_t size;
		uint8_t ed = PHY_GetEDLevel();

		rf_hw_spi_select();
		rf_hw_write_byte_spi(RF_CMD_FRAME_R);
		size = rf_hw_write_byte_spi(0);

		if(size < 128)
		{
			for (uint8_t i = 0; i < size + 2 /* lqi + ED */; i++)
				phyRxBuffer[i] = rf_hw_write_byte_spi(0);

			rf_hw_spi_deselect();

			if(phyWaitState(TRX_STATUS_RX_AACK_ON) == false)
				rf_app_critical_fail_indication(RF_ERROR_WAIT_STATE);

			if(phy_mode == PHY_DEVICE_MODE)
			{
				// data is only the payload, no header is required
				// all frames are received as data type with compressed pan ID
				if(((phyRxBuffer[0] == 0x61 && req_ack) || (phyRxBuffer[0] == 0x41 && !req_ack)) && phyRxBuffer[1] == 0x88)
				{
					bool rx_callback_call = false;

					if(phy_multicast)
						rx_callback_call = true;
					else
					{
						uint16_t temp_dst_addr = (phyRxBuffer[6] << 8) | phyRxBuffer[5];;
						//Check if sequence number of current frame is different from previous frame (Duplicate) - Broadcast is exception.
						if(temp_dst_addr != PHY_BROADCAST_ADDR)
						{
							if(phy_seq_num_rx != phyRxBuffer[2])
							{
								phy_seq_num_rx = phyRxBuffer[2];
								rx_callback_call = true;
							}
						}
						else
							rx_callback_call = true;
					}

					if(rx_callback_call)
					{
						rx_frame_header.size		= size-PHY_CRC_SIZE-PHY_HDR_COMP_PAN_ID_SIZE;
						rx_frame_header.seq_number  = phyRxBuffer[2];
						rx_frame_header.pan_id		= (phyRxBuffer[4] << 8) | phyRxBuffer[3];
						rx_frame_header.dst_addr	= (phyRxBuffer[6] << 8) | phyRxBuffer[5];
						rx_frame_header.src_addr	= (phyRxBuffer[8] << 8) | phyRxBuffer[7];
						rx_frame_header.lqi			= phyRxBuffer[rx_frame_header.size];
						rx_frame_header.ed			= ed;//phyRxBuffer[rx_frame_header.size+1];
						rx_frame_header.fcs_status	= PHY_GetFCSStatus();

						rf_app_rx_indication(&phyRxBuffer[PHY_HDR_COMP_PAN_ID_SIZE], rx_frame_header);
					}
				}
			}
			else
			{
				rx_frame_header.size		= size-PHY_CRC_SIZE;
				rx_frame_header.seq_number  = 0;
				rx_frame_header.pan_id		= 0;
				rx_frame_header.dst_addr	= 0;
				rx_frame_header.src_addr	= 0;
				rx_frame_header.lqi			= 0;
				rx_frame_header.ed			= 0;
				rx_frame_header.fcs_status	= PHY_GetFCSStatus();

				rf_app_rx_indication(phyRxBuffer, rx_frame_header);
			}
		}

	  if(always_rx_return_state == false)
		  phyTrxSetState(trx_cmd_return_state[return_state]);

		phyState = PHY_STATE_IDLE;
    }
    else if (PHY_STATE_TX_WAIT_END == phyState)
    {
      uint8_t status = (phyReadRegister(TRX_STATE_REG) >> TRAC_STATUS) & 7;

      if (TRAC_STATUS_SUCCESS == status || TRAC_STATUS_SUCCESS_DATA_PENDING == status)
        status = PHY_STATUS_SUCCESS;
      else if (TRAC_STATUS_CHANNEL_ACCESS_FAILURE == status)
        status = PHY_STATUS_CHANNEL_ACCESS_FAILURE;
      else if (TRAC_STATUS_NO_ACK == status)
        status = PHY_STATUS_NO_ACK;
      else
        status = PHY_STATUS_ERROR;

      if(always_rx_return_state == true)
    	  phySetRxState(true);
      else
    	  phyTrxSetState(trx_cmd_return_state[return_state]);

      phyState = PHY_STATE_IDLE;

      rf_app_tx_indication(status == PHY_STATUS_SUCCESS ? RF_APP_OK : RF_APP_ERROR);
    }
  }
}

void PHY_Interrupt(void)
{
	PHY_TaskHandler();
}

void phyForceSetRxState(void)
{
    phyReadRegister(IRQ_STATUS_REG);
    phyTrxSetState(TRX_CMD_RX_AACK_ON);
}

void phy_set_always_rx_mode(bool rx_state_return)
{
  always_rx_return_state = rx_state_return;
}
