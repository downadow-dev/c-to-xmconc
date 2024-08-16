#include "useful.h"

int stack[100];
int stackptr = 0;

void execute(char *command) {
    char buf[64];
    memset(buf, '\0', sizeof(buf));
    
    // copying command to clean buf
    for(int i = 0; i < sizeof(buf) && i < strlen(command); i++)
        buf[i] = command[i];
    
    // clear stackptr
    if(strlen(buf) == 0)
        stackptr = 0;
    // character
    else if(buf[0] == '\'')
        stack[stackptr++] = buf[1];
    // number
    else if(buf[0] >= (int)'0' && buf[0] <= (int)'9')
        stack[stackptr++] = atoi(buf);
    // print number
    else if(buf[0] == '.') {
        printf("%d\n", stack[--stackptr]);
        getc();
    }
    // print character
    else if(memcmp(buf, "emit", 5) == 0) {
        printf("%c\n", stack[--stackptr]);
        getc();
    }
    // addition...
    else if(buf[0] == '+') {
        stackptr -= 2;
        stack[stackptr] = stack[stackptr] + stack[stackptr + 1];
        
        stackptr++;
    }
    else if(buf[0] == '-') {
        stackptr -= 2;
        stack[stackptr] = stack[stackptr] - stack[stackptr + 1];
        
        stackptr++;
    }
    else if(buf[0] == '*') {
        stackptr -= 2;
        stack[stackptr] = stack[stackptr] * stack[stackptr + 1];
        
        stackptr++;
    }
    else if(buf[0] == '/') {
        stackptr -= 2;
        stack[stackptr] = stack[stackptr] / stack[stackptr + 1];
        
        stackptr++;
    }
    else if(buf[0] == '%') {
        stackptr -= 2;
        stack[stackptr] = stack[stackptr] % stack[stackptr + 1];
        
        stackptr++;
    }
    /* quit */
    else {
        exit(0);
    }
}

int main() {
    memset(stack, '\0', sizeof(stack));
    
    while(true) {
        clear_output();
        
        printf("[%d]> ", (stackptr > 0 ? stack[stackptr - 1] : 0));
        
        char buf[64];
        memset(buf, '\0', sizeof(buf));
        gets(buf, sizeof(buf));
        execute(buf);
    }
}

