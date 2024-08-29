#ifndef __gets_h
#define __gets_h   1

#include <misc.h>

char *gets(char *buf, int size) {
    int i, c;
    for(i = 0; i < (size - 1) && (c = getchar()) != '\n'; i++) {
        if(c != '\b') {
            buf[i] = c;
            printf("%c█\b", buf[i]);
        } else if(i > 0) {
            i -= 2;
            printf(" \b\b█\b");
        }
    }
    printf("\n");
    buf[i] = '\0';
    
    return buf;
}

bool strcmp(char *s1, char *s2) {
    if(strlen(s1) != strlen(s2))
        return false;
    
    for(int i = 0; s1[i] != '\0'; i++)
        if(s1[i] != s2[i])
            return false;
    
    return true;
}

#endif

