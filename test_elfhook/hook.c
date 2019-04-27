#include <stdio.h>
#include <stdlib.h>
#include "../include/hookelf.h"

INIT() {
    setbuf(stdout, NULL);
    puts("init");
}

HOOK(print) {
    static int count;

    printf("hook #%d: ", ++count);

    if (count >= 3)
        exit(0);
}
