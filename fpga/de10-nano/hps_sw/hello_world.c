#include <stdio.h>
#include <unistd.h>

int main() {
    int i = 0;
    while(1) {
        printf("Hello from DE10-Nano HPS! Count: %d\n", i++);
        sleep(1);
    }
    return 0;
}
