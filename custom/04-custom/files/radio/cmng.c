#include <zmq.h>
#include "app_cmng.h"
#include "cmng.h"

void* context = NULL;
void* c_publisher = NULL;
void* c_subscriber = NULL;

int cmng_init()
{
    context = zmq_ctx_new();

    c_subscriber = zmq_socket(context, ZMQ_SUB);
    if (cmng_init_subscriber() != CMNG_OK)
        return CMNG_ERROR;
    
    c_publisher = zmq_socket(context, ZMQ_PUB);
    if (cmng_init_publisher(1100000) != CMNG_OK)
        return CMNG_ERROR;

    return CMNG_OK;
}

int cmng_close()
{
    if(zmq_close(c_publisher) != CMNG_OK)
        return CMNG_ERROR;

    if(zmq_close(c_subscriber) != CMNG_OK)
        return CMNG_ERROR;

    return zmq_ctx_destroy(context);
}

int cmng_init_subscriber()
{
    zmq_connect(c_subscriber, "tcp://localhost:5555");
    return zmq_setsockopt(c_subscriber, ZMQ_SUBSCRIBE, "", 0);
}

int cmng_init_publisher(int sndhwm)
{
    zmq_setsockopt(c_publisher, ZMQ_SNDHWM, &sndhwm, sizeof(int));
    return zmq_bind(c_publisher, "tcp://*:5556");
}

int cmng_read(uint8_t* buf)
{
    int msg_size = zmq_recv(c_subscriber, buf, MAX_BUFFER_SIZE_MSG, 0);

    return msg_size;
}

int cmng_publish(uint8_t* p_buffer, int size)
{
    return zmq_send(c_publisher, p_buffer, size, 0);
}

