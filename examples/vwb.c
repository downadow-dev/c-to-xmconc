/* for Xmtwolime */


#include "useful.h"

int *mem = (void *)0;

int main() {
    char buf[128];
    getargs(buf);
    
    if((getuid() != 0 && atoi(buf) >= 8700000) || getuid() == 0 /* root */)
        printf("%d\n", mem[atoi(buf)]);
    else {
        printf("root required\n");
        return 1;
    }
}

