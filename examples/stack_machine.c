#include <useful.h>

int stack[100];
int stackptr = 0;

void execute(char *command) {
    char buf[64];
    memset(buf, '\0', sizeof(buf));
    
    if(stackptr < 0 || stackptr >= 100)
        exit(1);
    
    memcpy(buf, command, strlen(command) + 1);
    
    // clear stackptr
    if(strlen(buf) == 0)
        stackptr = 0;
    // character
    else if(buf[0] == '\'')
        stack[stackptr++] = buf[1];
    // number
    else if((buf[0] >= (int)'0' && buf[0] <= (int)'9') || (buf[1] >= (int)'0' && buf[1] <= (int)'9'))
        stack[stackptr++] = atoi(buf);
    // print number
    else if(strcmp(buf, ".")) {
        printf("%d\n", stack[--stackptr]);
        //getchar();
    }
    // print character
    else if(strcmp(buf, "emit")) {
        printf("%c\n", stack[--stackptr]);
        //getchar();
    }
    // addition...
    else if(strcmp(buf, "+")) {
        stackptr -= 2;
        stack[stackptr] = stack[stackptr] + stack[stackptr + 1];
        
        stackptr++;
    }
    else if(strcmp(buf, "-")) {
        stackptr -= 2;
        stack[stackptr] = stack[stackptr] - stack[stackptr + 1];
        
        stackptr++;
    }
    else if(strcmp(buf, "*")) {
        stackptr -= 2;
        stack[stackptr] = stack[stackptr] * stack[stackptr + 1];
        
        stackptr++;
    }
    else if(strcmp(buf, "/")) {
        stackptr -= 2;
        stack[stackptr] = stack[stackptr] / stack[stackptr + 1];
        
        stackptr++;
    }
    else if(strcmp(buf, "mod")) {
        stackptr -= 2;
        stack[stackptr] = stack[stackptr] % stack[stackptr + 1];
        
        stackptr++;
    }
    /* quit */
    else if(strcmp(buf, "bye"))
        exit(0);
    /* unknown command */
    else {
        printf("?\n");
        //sleep(1);
    }
}

int main() {
    memset(stack, '\0', sizeof(stack));
    
    while(true) {
        //clear_output();
        
        printf("> ");
        
        char buf[64];
        memset(buf, '\0', sizeof(buf));
        gets(buf, sizeof(buf));
        execute(buf);
    }
}

