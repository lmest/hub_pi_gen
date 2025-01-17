#include <stdbool.h>
#include <stdint.h>
#include "cbf.h"

#define CBF_INC(v,mv)   ((((v) + 1) >= (mv)) ? 0 : (v) + 1)

cbf_status_t cbf_init(cbf_t* cb, uint8_t* area, uint16_t size)
{
	cb->buffer = area;
	cb->size = size;
	cb->prod = cb->cons = 0;

	return CBF_OK;
}

uint16_t cbf_bytes_available(cbf_t* cb)
{
	if (cb->prod >= cb->cons)
		return cb->prod - cb->cons;
	else
		return cb->prod + (cb->size - cb->cons);
}

cbf_status_t cbf_flush(cbf_t* cb)
{
	cb->prod = cb->cons = 0;

	return CBF_OK;
}

cbf_status_t cbf_get(cbf_t* cb, uint8_t* c)
{
	if (cb->cons == cb->prod)
		return CBF_EMPTY;

	*c = cb->buffer[cb->cons];
	cb->cons = CBF_INC(cb->cons, cb->size);

	return CBF_OK;
}

cbf_status_t cbf_put(cbf_t* cb, uint8_t c)
{
	uint16_t next_prod = CBF_INC(cb->prod, cb->size);

	if (next_prod == cb->cons)
		return CBF_FULL;

	cb->buffer[cb->prod] = c;
	cb->prod = next_prod;

	return CBF_OK;
}