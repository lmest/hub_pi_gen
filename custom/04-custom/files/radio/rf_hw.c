#include "phy.h"
#include "hw.h"

void rf_hw_set_irq(void)
{
	PHY_Interrupt();
}

void rf_hw_reset(void)
{
	hw_at86_rst_clear();
	hw_timer_delay_ms(2);
	hw_at86_rst_set();
}

void rf_hw_disable_irq(void)
{
	hw_at86_disable_irq();
}

void rf_hw_enable_irq(void)
{
	hw_at86_enable_irq();
}

uint8_t rf_hw_write_byte_spi(uint8_t tx_data)
{
	return hw_at86_spi_write_byte(tx_data);
}

void rf_hw_rst_clear(void)
{
	hw_at86_rst_clear();
}

void rf_hw_rst_set(void)
{
	hw_at86_rst_set();
}

void rf_hw_spi_select(void)
{
	hw_at86_spi_select();
}

void rf_hw_spi_deselect(void)
{
	hw_at86_spi_deselect();
}

void rf_hw_slp_tr_set(void)
{
	hw_at86_slp_tr_set();
}

void rf_hw_slp_tr_clear(void)
{
	hw_at86_slp_tr_clear();
}


