/*
 * rf_hw.h
 *
 *  Created on: 20 de set de 2019
 *      Author: LMEst
 */

#ifndef RF_HW_H_
#define RF_HW_H_

void rf_hw_set_irq(void);
void rf_hw_reset(void);
void rf_hw_disable_irq(void);
void rf_hw_enable_irq(void);
uint8_t rf_hw_write_byte_spi(uint8_t tx_data);
void rf_hw_rst_clear(void);
void rf_hw_rst_set(void);
void rf_hw_spi_select(void);
void rf_hw_spi_deselect(void);
void rf_hw_slp_tr_set(void);
void rf_hw_slp_tr_clear(void);

#endif /* RF_HW_H_ */
