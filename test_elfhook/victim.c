#include <stdio.h>
#include <unistd.h>

void print(void) {
    asm("nop;nop;nop;nop");
    puts("victim");
}

int main(void) {
    setbuf(stdout, NULL);
    puts("victim starting");
    for (int i = 0; i < 10; i++)
        print();
    return 0;
}
