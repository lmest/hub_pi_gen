/**
 * \file phy.h
 *
 * \brief AT86RF233 PHY interface
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
 * $Id: phy.h 9267 2014-03-18 21:46:19Z ataradov $
 *
 */

#ifndef _PHY_H_
#define _PHY_H_

/*- Includes ---------------------------------------------------------------*/
#include <stdint.h>
#include <stdbool.h>

/*- Definitions ------------------------------------------------------------*/
#define PHY_BROADCAST_ADDR						0xFFFF
#define PHY_CRC_SIZE    						2
#define PHY_HDR_COMP_PAN_ID_SIZE 				(2+1+2+2+2)  // FC(2)+SN(1)+DPANID(2)+DADDR(2)+SADDR(2)
#define PHY_MAX_CYCLES_TO_WAIT_RADIO_STATE		10000
#define PHY_RSSI_BASE_VAL                     	(-91)

#define PHY_HAS_RANDOM_NUMBER_GENERATOR
#define PHY_HAS_AES_MODULE

/*- Types ------------------------------------------------------------------*/
typedef struct PHY_DataInd_t
{
  uint8_t    *data;
  uint8_t    size;
  uint8_t    lqi;
  int8_t     rssi;
} PHY_DataInd_t;

typedef struct PHY_Frame_Header_Fields_s
{
	uint8_t size;
	uint8_t seq_number;
	uint16_t pan_id;
	uint16_t dst_addr;
	uint16_t src_addr;
	uint8_t lqi;
	uint8_t ed;
	uint8_t fcs_status;
} PHY_Frame_Header_Fields_t;

enum
{
  PHY_STATUS_SUCCESS                = 0,
  PHY_STATUS_CHANNEL_ACCESS_FAILURE = 1,
  PHY_STATUS_NO_ACK                 = 2,
  PHY_STATUS_ERROR                  = 3,
};

typedef enum rf_send_status_e
{
	RF_APP_SEND_OK 		  = 0,
	RF_APP_SEND_RADIO_BUSY    = 1,
	RF_APP_SEND_FAIL_RADIO    = 2,
} rf_send_status_t;


typedef enum PHY_OperationMode_e
{
	PHY_DEVICE_MODE,
	PHY_SNIFFER_MODE,
	PHY_PROMISCUOUS_MODE,
	PHY_SITE_SURVEY_CCA,
} PHY_OperationMode_t;

typedef enum
{
  PHY_RETURN_STATE_TRX_OFF = 0,
  PHY_RETURN_STATE_TX,
  PHY_RETURN_STATE_RX,
} PhyReturnState_t;

typedef enum PHY_CCA_Mode_e
{
	CCA_MODE_3A = 0,
	CCA_MODE_1,
	CCA_MODE_2,
	CCA_MODE_3B
} PHY_CCA_Mode_t;

typedef enum PHY_External_Clock_e
{
	CLKM_NONE = 0,
	CLKM_1MHZ,
	CLKM_2MHZ,
	CLKM_4MHZ,
	CLKM_8MHZ,
	CLKM_16MHZ,
	CLKM_250KHZ,
	CLKM_62_5KHZ
} PHY_External_Clock_t;

/*- Prototypes -------------------------------------------------------------*/
void PHY_Init(PHY_OperationMode_t mode);
void PHY_SetReducedPowerMode(bool enable_reduced_power);
void PHY_SetRxState(bool rx, bool auto_ack_retr);
void PHY_SetDIGExternal(void);
void PHY_DisableClockExternalOutput(void);
void PHY_EnableClockExternalOutput(PHY_External_Clock_t clk_freq);
void PHY_SetChannel(uint8_t channel);
void PHY_SetPanId(uint16_t panId);
void PHY_SetShortAddr(uint16_t addr);
void PHY_SetTxPower(uint8_t txPower);
void PHY_Set_Rx_Sensitivity_Threshold(uint8_t threshold);
void PHY_Set_CCA_Mode(PHY_CCA_Mode_t cca_mode);
void PHY_Set_CCA_Threshold(uint8_t threshold);
void PHY_GetCSMABackoff(uint8_t *min_be,uint8_t *max_be);
void PHY_SetCSMABackoff(uint8_t min_be,uint8_t max_be);
void PHY_SetMaxFrameRetries(uint8_t max_ret);
void PHY_SetMaxCSMARetries(uint8_t max_ret);
uint8_t PHY_GetFrameRetries(void);
uint8_t PHY_GetCSMARetries(void);
void PHY_SetACKTime(bool ack_time);
void PHY_Enable_ACK(void);
void PHY_Disable_ACK(void);
void PHY_Set_Multicast(bool multicast);
void PHY_Set_Init_Mode(bool rx_state_return);
void PHY_Set_State_to_Return(PhyReturnState_t state_to_return);
void PHY_Sleep(void);
void PHY_DeepSleep(void);
void PHY_Wakeup(void);
rf_send_status_t PHY_DataReq(uint8_t *data, uint8_t size, uint16_t pan_id_addr, uint16_t dst_addr, bool app_retx);
void PHY_DataConf(uint8_t status);
void PHY_DataInd(PHY_DataInd_t *ind);
void PHY_TaskHandler(void);
uint8_t PHY_ReadPartNumber(void);
uint8_t PHY_ReadChipID(void);
uint8_t PHY_ReadDataRate(void);
void PHY_SetDataRate(uint8_t data_rate);
void PHY_Interrupt(void);
void PHY_DisableRxPath(void);
void PHY_EnableRxPath(void);
void PHY_Set_CCA_Request(void);
uint8_t PHY_GetChannel(void);
uint8_t PHY_Get_CCA_Threshold(void);
uint8_t PHY_ReadIRQStatus(void);
uint16_t PHY_GetShortAddr(void);
uint16_t PHY_GetPanId(void);
uint8_t PHY_GetDataRate(void);
uint8_t PHY_GetTxPower(void);
uint8_t PHY_GetRSSI(void);
uint8_t PHY_GetFCSStatus(void);
void PHY_SetPAExtCtrl(bool state);

uint8_t PHY_GetNextSeqNumber(bool app_retx);
bool phyTrxSetState(uint8_t state);

void phyForceSetRxState(void);
void phy_set_always_rx_mode(bool rx_state_return);

#ifdef PHY_ENABLE_RANDOM_NUMBER_GENERATOR
uint16_t PHY_RandomReq(void);
#endif

#ifdef PHY_ENABLE_AES_MODULE
void PHY_EncryptReq(uint8_t *text, uint8_t *key);
#endif

#ifdef PHY_ENABLE_ENERGY_DETECTION
int8_t PHY_EdReq(void);
#endif

#endif // _PHY_H_
