#pragma once

#define APP_BUFFER_MAX 11000
#define MAX_BUFFER_SIZE_MSG 200
#define MSG_PAYLOAD_SIZE 13

#define FILTER_LIST_MAX_ITENS 20
#define PID_SIZE 12
#define PID_SIZE_BYTES 4
#define NEXT_PID_POS 13

#define SEND_COMFIRMATION_OK 0
#define SEND_COMFIRMATION_ERROR 1

#define TX_OK 0
#define TX_ERROR 1
#define TX_WAITING_CBK 2

#define ZIGBEE_MAX_SIZE 127
#define MAX_RETRIES_TX 5
#define MAX_RETRIES_TX_RESET 2
#define PAYLOAD_DATA_BEACON_SENSOR 16

#define GLOBAL_BEACON_MSG_SIZE 29
#define BEACON_MSG_SIZE 1
#define DATA_SEG_MSG_SIZE 115
#define BEACON_BCI_SIZE 19
#define ZIGBEE_NETWORK_CHECKIN 13

/*Server to Radio*/
typedef enum msg_type_e {
	NEW_FILTER_LIST = 0,
	MSG_TO_SEND,
	RESET_GPIO,
	SERVER_STATUS,		
}msg_type_t;

typedef struct msg_filter_s
{
	uint8_t num_inputs;
	uint8_t buffer[MAX_BUFFER_SIZE_MSG];
}msg_filter_t;

typedef struct msg2send_s
{
	uint8_t msg_num;
	uint8_t zid;
	uint8_t size;
	uint8_t buffer[MAX_BUFFER_SIZE_MSG];
}msg2send_t;

typedef struct msg_radio_s
{
	uint8_t radio_cmd;
	uint8_t zid;
	uint8_t pid[PID_SIZE];
	uint8_t msg_size;		
	uint8_t buffer[MAX_BUFFER_SIZE_MSG];
}msg_radio_t;

typedef struct filter_list_s
{
	char pid[PID_SIZE];
	uint8_t zid;
	uint16_t seq_number;
}filter_list_t;

/*Radio to Server*/
typedef enum rf_cmd_id_e
{
    RF_CMD_BEACON_GLOBAL_DATA = 0x01, 
    RF_CMD_BEACON, 
    RF_CMD_DATA_REQ,
    RF_CMD_DATA_SEG_VIB,
    RF_CMD_DATA_SEG_AUD,
    RF_CMD_DATA_CHECK_VIB,
    RF_CMD_DATA_CHECK_AUD,
	RF_CMD_KEEP_ALIVE,
	RF_CMD_COMMISSIONING_REQ,
	RF_CMD_COMMISSIONING_ANS,	
	RF_SEND_CONFIRMATION,
	RF_SERVER_STATUS_REPLY,
	RF_CMD_FAULT_DETECT,
	RF_CMD_BEACON_SATO,
	RF_CMD_SATO_CONTROL,
	RF_CMD_BEACON_MTSS,
	RF_CMD_DATA_BCI,
	RF_CMD_ECHO,
	RF_CMD_ZIGBEE_NETWORK_CHECKIN,
} rf_cmd_id_t;

typedef enum pid_check_filter_list_e {
	ITEM_NOT_FOUND = 0,
	ITEM_FOUND,
}pid_check_filter_list_e;

void app_cmng_init(void);

void app_cmng_put_in_cbf(uint8_t* buffer_in, uint8_t msg_size);
void app_cmng_get_msg_type(uint8_t* p_buffer);
void app_cmng_get_in_msg2send_cbf(msg2send_t* buffer_in);
void app_cmng_get_in_filter_cbf(msg_filter_t *read_msg_in);
uint16_t app_cmng_cbf_in_bytes_available(void);
uint16_t app_cmng_cbf_in_bytes_available(void);
uint16_t app_cmng_cbf_out_bytes_available(void);

void app_cmng_new_filter_list(void);
int app_cmng_verify_filter_list_pid(msg_radio_t* radio_msg, uint16_t *scr_addr);
int app_cmng_verify_filter_list_zid(uint16_t *zid_scr_addr);
void app_cmng_msg_to_send(void);
void app_cmng_print_radio_param(msg_radio_t *rad_msg);

void app_cmng_filter_in(void);
void app_cmng_filter_out(uint8_t* radio_buffer, uint8_t buff_size, uint16_t src_adress);
void app_cmng_set_pan_id(uint16_t pan_id_ini);