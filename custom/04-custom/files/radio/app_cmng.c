#include <zmq.h>
#include <string.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include "cbf.h"
#include "app_cmng.h"
#include "cmng.h"
#include "hw.h"
#include "phy.h"
#include "rf_app.h"
#include "buf_io.h"
#include "app.h"

#define PRINT_SENSOR_ID_ECHO    0
#define DELAY_WAIT_ACK_MS       2000

cbf_t cbf_in;
uint8_t cbf_area_in[APP_BUFFER_MAX];
filter_list_t filter_list[FILTER_LIST_MAX_ITENS];
uint8_t filter_list_num_itens = 1;
uint16_t radio_pan_id = 0;

void app_cmng_init(void)
{
    cbf_init(&cbf_in, cbf_area_in, APP_BUFFER_MAX);
}

void app_cmng_put_in_cbf(uint8_t* buffer_in, uint8_t msg_size)
{
    for (int msg_pos = 0; msg_pos < msg_size; msg_pos++)
    {
        cbf_put(&cbf_in, buffer_in[msg_pos]);
    }
}

void app_cmng_get_msg_type(uint8_t* p_buffer)
{
    cbf_get(&cbf_in, p_buffer); 
}

void app_cmng_get_in_msg2send_cbf(msg2send_t* buffer_in)
{
    cbf_get(&cbf_in, &buffer_in->zid);
    cbf_get(&cbf_in, &buffer_in->msg_num);
    cbf_get(&cbf_in, &buffer_in->size);

    printf("|\n| Msg to Send: ZID[%u] - MSG_NUM[%u] - SIZE[%u]\n|\n", buffer_in->zid, buffer_in->msg_num, buffer_in->size);

    for (uint8_t msg_pos = 0; msg_pos < (buffer_in->size); msg_pos++)
    {
        cbf_get(&cbf_in, &buffer_in->buffer[msg_pos]);
        printf("%u ", buffer_in->buffer[msg_pos]);
    }
    printf("\n|\n");
}

void app_cmng_get_in_filter_cbf(msg_filter_t *read_msg_in)
{
    cbf_get(&cbf_in, &read_msg_in->num_inputs);
    
    for (uint8_t item_num = 0; item_num < (read_msg_in->num_inputs); item_num++)
    {
        for (uint8_t msg_pos = 0; msg_pos < MSG_PAYLOAD_SIZE; msg_pos++)
        {
            cbf_get(&cbf_in, &read_msg_in->buffer[msg_pos + (item_num * MSG_PAYLOAD_SIZE)]);
        }
    }
}

uint8_t app_cmng_get_in_server_status()
{
    uint8_t server_status = 0;

    cbf_get(&cbf_in, &server_status);

    return server_status;
}

uint16_t app_cmng_cbf_in_bytes_available(void)
{
    return cbf_bytes_available(&cbf_in);
}


void app_cmng_new_filter_list(void)
{
    msg_filter_t new_msg;
    uint8_t fl_pos = 0;
    
    app_cmng_get_in_filter_cbf(&new_msg);

    for (uint8_t num_item_add = filter_list_num_itens; num_item_add < new_msg.num_inputs; num_item_add++)
    {
        for (fl_pos = 0; fl_pos < PID_SIZE; fl_pos++)
        {
            filter_list[num_item_add].pid[fl_pos] = new_msg.buffer[fl_pos + (num_item_add*NEXT_PID_POS)];
        }        
        filter_list[num_item_add].zid = new_msg.buffer[fl_pos + (num_item_add*NEXT_PID_POS)];
    }
 }

uint8_t app_cmng_send_frame(uint8_t *buffer, uint8_t payload_size, uint16_t destiny_addr, bool app_retransmission)
{
    uint8_t retries = 0;
    rf_send_status_t send_status = RF_APP_SEND_RADIO_BUSY;

    while((send_status == RF_APP_SEND_RADIO_BUSY) && (retries < MAX_RETRIES_TX))
    {
		send_status = rf_app_tx_data(buffer,payload_size,radio_pan_id,destiny_addr,app_retransmission);
        retries++;
	}
	
	if(send_status != RF_APP_SEND_OK)
    {
        printf("|\n| Transmission Error: Restarting Radio! \n");
        app_radio_restart();
    }
		   
    return send_status;
}

void app_cmng_msg_to_send(void)
{
    msg2send_t new_msg2send;
    uint8_t send_confirmation[4]={RF_SEND_CONFIRMATION,1,1,TX_ERROR};
    extern volatile uint8_t tx_status;
    uint8_t retries = 0;

    app_cmng_get_in_msg2send_cbf(&new_msg2send);

    send_confirmation[1] = new_msg2send.zid;
    send_confirmation[2] = new_msg2send.msg_num;

    for (uint8_t fl_pos = 1; fl_pos <= filter_list_num_itens; fl_pos++)
    {
        if (filter_list[fl_pos].zid == new_msg2send.zid)
        {           
            tx_status = TX_WAITING_CBK;  

            while((tx_status != TX_OK) && (retries <= MAX_RETRIES_TX_RESET))
            {
                tx_status = TX_WAITING_CBK;
                
                app_cmng_send_frame(new_msg2send.buffer, new_msg2send.size, filter_list[fl_pos].seq_number, false);

                uint32_t start_time = hw_timer_get_tick_ms();                
                while ((tx_status == TX_WAITING_CBK) && (hw_timer_elapsed_ms(start_time) < DELAY_WAIT_ACK_MS));
                
                retries++;
            }

            send_confirmation[3] = tx_status;            
            cmng_publish(send_confirmation, 4);
            
            if(tx_status == TX_OK)       
                hw_timer_wait_reset();  
            
            return;
        }
    }
    cmng_publish(send_confirmation,4);   
}

void app_cmng_filter_in(void)
{
    uint8_t buff_msg_type;
    extern volatile uint8_t status_server;
    
    app_cmng_get_msg_type(&buff_msg_type);    

    switch (buff_msg_type)
    {
    case NEW_FILTER_LIST:
        printf("|\n| New Filter List\n|\n");
        app_cmng_new_filter_list();
        break;
    
    case MSG_TO_SEND:
        hw_at86_disable_irq();
        //printf("|\n| Mesage to Send|\n");
        app_cmng_msg_to_send();
        break;

    case RESET_GPIO:
        printf("|\n| Reset GPIO\n|\n");
        rpi_reset();
        break;

    case SERVER_STATUS:
        status_server = app_cmng_get_in_server_status();
        printf("|\n| Server Connection Status: %d\n|\n", status_server);
        rpi_gpio_on(RPI_LED3_GPIO);
        rpi_gpio_off(RPI_LED2_GPIO);
        rpi_gpio_off(RPI_LED1_GPIO);

        uint8_t server_reply[1] = {RF_SERVER_STATUS_REPLY};
        cmng_publish(server_reply, 1);
        break;

    default:
        break;
    }
}

int app_cmng_verify_filter_list_pid(msg_radio_t* radio_msg, uint16_t *scr_addr)
{
    for (uint8_t item_pos = 1; item_pos <= filter_list_num_itens; item_pos++)
    {
        if(memcmp(radio_msg->pid,filter_list[item_pos].pid,12) == 0)
        {
            radio_msg->zid = filter_list[item_pos].zid;
            filter_list[item_pos].seq_number = *scr_addr;
            return ITEM_FOUND;
        }       
    }

    radio_msg->zid = filter_list_num_itens;
    filter_list[filter_list_num_itens].zid = filter_list_num_itens;
    filter_list[filter_list_num_itens].seq_number = *scr_addr;

    printf("|\n| New Sensor Added - ZID[%u] - PID:[ ", filter_list_num_itens);    
    for (uint8_t fl_pos = 0; fl_pos < PID_SIZE; fl_pos++)
    {
        filter_list[filter_list_num_itens].pid[fl_pos] = radio_msg->pid[fl_pos];
        printf("%u ", filter_list[filter_list_num_itens].pid[fl_pos]);
    }
    printf("]\n|\n");    

    filter_list_num_itens++;

    return ITEM_NOT_FOUND;
}

int app_cmng_verify_filter_list_zid(uint16_t *zid_scr_addr)
{
    int status = ITEM_NOT_FOUND;

    for (uint8_t item_pos = 1; item_pos <= filter_list_num_itens; item_pos++)
    {
        if(filter_list[item_pos].zid == *zid_scr_addr)
        {
            filter_list[item_pos].seq_number = *zid_scr_addr;
            status = ITEM_FOUND;
            break;
        }       
    }

    return status;
}

void app_cmng_filter_out(uint8_t *radio_buffer, uint8_t buff_size, uint16_t src_adress)
{
    msg_radio_t new_msg_radio;
    uint8_t buffer_out[ZIGBEE_MAX_SIZE];
    uint8_t msg_size = 0;
    static uint8_t num_beacons = 1;

    new_msg_radio.radio_cmd = buf_io_get8_fl(radio_buffer);

    if (new_msg_radio.radio_cmd == RF_CMD_BEACON_GLOBAL_DATA)
    {
        if (buff_size == GLOBAL_BEACON_MSG_SIZE)
        {
            radio_buffer += 1;
            memcpy(new_msg_radio.pid, radio_buffer, 12);
            radio_buffer -= 1;

            app_cmng_verify_filter_list_pid(&new_msg_radio, &src_adress);
            radio_buffer[buff_size] = new_msg_radio.zid;

            radio_buffer[buff_size+1] = num_beacons;

            if(num_beacons + 1 > 255)
                num_beacons = 1;
            else
                num_beacons += 1;    

            cmng_publish(radio_buffer, buff_size + 2);
            
            printf("|\n| New Beacon: %u\n|\n", buff_size);  
        }
    }
    else if (new_msg_radio.radio_cmd == RF_CMD_DATA_BCI)
    {
        if (buff_size == BEACON_BCI_SIZE)
        {
            radio_buffer += 1;
            memcpy(new_msg_radio.pid, radio_buffer, 12);
            radio_buffer -= 1;

            app_cmng_verify_filter_list_pid(&new_msg_radio, &src_adress);
            radio_buffer[buff_size] = new_msg_radio.zid;

            radio_buffer[buff_size+1] = num_beacons;

            if(num_beacons + 1 > 255)
                num_beacons = 1;
            else
                num_beacons += 1;    

            cmng_publish(radio_buffer, buff_size + 2);
            
            printf("|\n| New Beacon: %u\n|\n", buff_size);  
        }
    }
    else if (new_msg_radio.radio_cmd == RF_CMD_BEACON)
    {
        if (buff_size == BEACON_MSG_SIZE)
        {
            app_cmng_verify_filter_list_zid(&src_adress);

            buffer_out[0] = new_msg_radio.radio_cmd;
            buffer_out[1] = src_adress;

            cmng_publish(buffer_out, 2);
        }
    }
    else if ((new_msg_radio.radio_cmd == RF_CMD_DATA_SEG_VIB) || (new_msg_radio.radio_cmd == RF_CMD_DATA_SEG_AUD))
    {
        if (buff_size == DATA_SEG_MSG_SIZE && src_adress <= filter_list_num_itens)
        {
            app_cmng_verify_filter_list_zid(&src_adress);

            buffer_out[0] = new_msg_radio.radio_cmd;
            buffer_out[1] = src_adress;
            buffer_out[2] = buff_size - 3;
            msg_size += 3;

            for (int msg_pos = 1; msg_pos < buff_size; msg_pos++)
            {
                buffer_out[msg_size] = radio_buffer[msg_pos];
                msg_size++;
            }

            cmng_publish(buffer_out, msg_size);
        }
    }
    else if (new_msg_radio.radio_cmd == RF_CMD_FAULT_DETECT)
    {
        printf("| FAULT DETECT CMD\n");
        printf("| SENSOR ID: ");
        for (int msg_pos = 1; msg_pos <= 12; msg_pos++)
        {
            printf("%u ", radio_buffer[msg_pos]);
        }
        printf("\n");
        
        printf("| DATA: ");
        for (int msg_pos = 13; msg_pos < buff_size; msg_pos+=4)
        {
            printf("%02X%02X%02X%02X ", radio_buffer[msg_pos+3],radio_buffer[msg_pos+2],radio_buffer[msg_pos+1],radio_buffer[msg_pos]);
        }
        printf("\n");
    }
    else if (new_msg_radio.radio_cmd == RF_CMD_ECHO)
    {
        radio_buffer += 1;
        memcpy(new_msg_radio.pid, radio_buffer, 12);
        radio_buffer -= 1;

        app_cmng_verify_filter_list_pid(&new_msg_radio, &src_adress);
        
        printf("| ECHO CMD -> SRC: %d | SIZE:%d\n", src_adress, buff_size);

#if PRINT_SENSOR_ID_ECHO == 1
        printf("| SENSOR ID: ");
        for (int msg_pos = 1; msg_pos <= 12; msg_pos++)
        {
            printf("%u ", radio_buffer[msg_pos]);
        }
        printf("\n");
#endif

        uint8_t buff_send_req[4] = {MSG_TO_SEND, new_msg_radio.zid, 1, buff_size} ;
        app_cmng_put_in_cbf(buff_send_req, 4);
        app_cmng_put_in_cbf(radio_buffer, buff_size);
    }
    else if (new_msg_radio.radio_cmd == RF_CMD_ZIGBEE_NETWORK_CHECKIN)
    {
        if (buff_size == ZIGBEE_NETWORK_CHECKIN)
        {
            radio_buffer += 1;
            memcpy(new_msg_radio.pid, radio_buffer, 12);
            radio_buffer -= 1;

            app_cmng_verify_filter_list_pid(&new_msg_radio, &src_adress);
            radio_buffer[buff_size] = new_msg_radio.zid;

            cmng_publish(radio_buffer, buff_size + 1);
            
            printf("|\n| ZIGBEE UPDATE CHECK-IN: %u\n|\n", buff_size); 
        }
    }
    else
    {
        printf("| INVALID CMD: ");
        for (int msg_pos = 0; msg_pos < buff_size; msg_pos++)
        {
            printf("%u ", radio_buffer[msg_pos]);
        }
        printf("\n|");
    }    
}

void app_cmng_set_pan_id(uint16_t pan_id_ini)
{
    radio_pan_id = pan_id_ini;
}