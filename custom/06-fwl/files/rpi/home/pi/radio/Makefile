#
# Set CROSS_PREFIX to prepend to all compiler tools at once for easier
# cross-compilation.
CROSS_PREFIX =

CC = $(CROSS_PREFIX)gcc

CFLAGS  += -O2 -Wall -pthread -pedantic -std=c11 -D_GNU_SOURCE -I/usr/include -I/include
LDFLAGS += -Wall -lrt -lpthread -lm -lpigpio -lzmq -L/usr/lib/ -L/usr/lib/arm-linux-gnueabihf 

SRC = app.c hw.c phy.c rf_app.c rf_hw.c buf_io.c cmng.c cbf.c app_cmng.c ini.c
OBJ = $(patsubst %.c, %.o, $(SRC))
TARGET = fwl_hub

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $^ -o $@ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	-rm $(OBJ) $(TARGET)

install: $(TARGET)
	install -D -m 0755 $(TARGET) /home/pi/radio/$(TARGET)

.PHONY: all install

