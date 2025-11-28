CC = arm-linux-gnueabihf-gcc
CFLAGS = -static -O2 -Wall

all: bridge_server

bridge_server: bridge_server.c
	$(CC) $(CFLAGS) -o bridge_server bridge_server.c -lm

clean:
	rm -f bridge_server
