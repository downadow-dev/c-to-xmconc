#include "useful.h"

int main() {
    char buf[64];
    gets(buf, sizeof(buf));
    
    printf("\n");
    for(int i = 0; i < strlen(buf); i++)
        printf("%c\t%d\n", buf[i], buf[i]);
}

