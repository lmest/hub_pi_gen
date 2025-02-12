#pragma once

#define CMNG_OK 0
#define CMNG_ERROR -1

int cmng_init();
int cmng_close();
int cmng_init_subscriber();
int cmng_init_publisher(int sndhwm);
int cmng_read(uint8_t* buf);
int cmng_publish(uint8_t* p_buffer, int size);
