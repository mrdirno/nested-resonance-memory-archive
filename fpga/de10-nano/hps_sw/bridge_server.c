#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>
#include <errno.h>
#include <stdint.h>
#include <signal.h>

#define HW_REGS_BASE (0xFF200000)
#define HW_REGS_SPAN (0x00200000)
#define HW_REGS_MASK (HW_REGS_SPAN - 1)
#define PORT 5000
#define BUFFER_SIZE 1024

void *virtual_base = MAP_FAILED;
int server_fd = 0, client_fd = 0;

void cleanup() {
    if (virtual_base != MAP_FAILED) {
        munmap(virtual_base, HW_REGS_SPAN);
        virtual_base = MAP_FAILED;
    }
    if (client_fd > 0) {
        close(client_fd);
        client_fd = 0;
    }
    if (server_fd > 0) {
        close(server_fd);
        server_fd = 0;
    }
}

void handle_sigint(int sig) {
    printf("\nTerminating bridge server...\n");
    cleanup();
    exit(0);
}

void process_command(int sock, char *buffer) {
    char response[BUFFER_SIZE];
    char *cmd = strtok(buffer, " \n\r");
    
    if (!cmd) return;

    if (strcmp(cmd, "PING") == 0) {
        snprintf(response, BUFFER_SIZE, "PONG\n");
    } else if (strcmp(cmd, "WR") == 0) {
        char *offset_str = strtok(NULL, " \n\r");
        char *value_str = strtok(NULL, " \n\r");
        
        if (offset_str && value_str) {
            uint32_t offset = strtoul(offset_str, NULL, 0);
            uint32_t value = strtoul(value_str, NULL, 0);
            
            if (offset < HW_REGS_SPAN) {
                volatile uint32_t *addr = (uint32_t *)((char *)virtual_base + offset);
                *addr = value;
                snprintf(response, BUFFER_SIZE, "OK\n");
            } else {
                snprintf(response, BUFFER_SIZE, "ERR: Offset out of range\n");
            }
        } else {
            snprintf(response, BUFFER_SIZE, "ERR: Missing arguments\n");
        }
    } else if (strcmp(cmd, "RD") == 0) {
        char *offset_str = strtok(NULL, " \n\r");
        
        if (offset_str) {
            uint32_t offset = strtoul(offset_str, NULL, 0);
            
            if (offset < HW_REGS_SPAN) {
                volatile uint32_t *addr = (uint32_t *)((char *)virtual_base + offset);
                uint32_t val = *addr;
                snprintf(response, BUFFER_SIZE, "0x%08X\n", val);
            } else {
                snprintf(response, BUFFER_SIZE, "ERR: Offset out of range\n");
            }
        } else {
            snprintf(response, BUFFER_SIZE, "ERR: Missing arguments\n");
        }
    } else {
        snprintf(response, BUFFER_SIZE, "ERR: Unknown command\n");
    }

    send(sock, response, strlen(response), 0);
}

int main() {
    int mem_fd;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    char buffer[BUFFER_SIZE];

    signal(SIGINT, handle_sigint);

    // 1. Map Memory
    printf("Opening /dev/mem...\n");
    if ((mem_fd = open("/dev/mem", O_RDWR | O_SYNC)) == -1) {
        perror("ERROR: could not open /dev/mem");
        return 1;
    }

    printf("Mapping memory...\n");
    virtual_base = mmap(NULL, HW_REGS_SPAN, (PROT_READ | PROT_WRITE), MAP_SHARED, mem_fd, HW_REGS_BASE);
    if (virtual_base == MAP_FAILED) {
        perror("ERROR: mmap() failed");
        close(mem_fd);
        return 1;
    }
    close(mem_fd); // File descriptor no longer needed after mmap

    printf("Memory mapped at %p\n", virtual_base);

    // 2. Setup Socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        cleanup();
        return 1;
    }

    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt))) {
        perror("setsockopt");
        cleanup();
        return 1;
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        cleanup();
        return 1;
    }

    if (listen(server_fd, 3) < 0) {
        perror("listen");
        cleanup();
        return 1;
    }

    printf("Bridge Server listening on port %d\n", PORT);

    // 3. Server Loop
    while (1) {
        printf("Waiting for connection...\n");
        if ((client_fd = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
            perror("accept");
            continue;
        }
        
        printf("New connection accepted\n");

        while (1) {
            memset(buffer, 0, BUFFER_SIZE);
            int valread = read(client_fd, buffer, BUFFER_SIZE - 1);
            if (valread <= 0) {
                break; // Connection closed or error
            }
            process_command(client_fd, buffer);
        }
        
        close(client_fd);
        client_fd = 0;
        printf("Connection closed\n");
    }

    cleanup();
    return 0;
}
