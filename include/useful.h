#ifndef __useful_h
#ifdef  __XCC_C__

#define __useful_h   1

#include <misc.h>

char *strchr(char *s, int c) {
    char *p = s;
    
    while(*p && *p != c) p++;
    
    return *p ? p : NULL;
}

int atoi(char *s) {
    char s2[8];
    memset(s2, '\0', sizeof(s2));
    
    int j;
    if(s[0] == '-' || s[0] == '+')
        j = 1;
    else
        j = 0;
    for(int i = (sizeof(s2) - strlen(s) - ((s[0] == '-' || s[0] == '+') ? 0 : 1)); i < (sizeof(s2) - 1) && j < strlen(s); i++)
        s2[i] = s[j++] - (int)'0';
    
    int num = cat(s2[1], s2[2], s2[3], s2[4],
        s2[5], s2[6]) + (1000000 * s2[0]);
    
    if(s[0] == '-')
        num = -num;
    
    return num;
}


#endif
#endif
