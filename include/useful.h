#ifndef __useful_h
#ifdef  __XCC_C__

#define __useful_h   1

#include <misc.h>


char *memset(char *buf, int c, size_t size) {
    char *p = buf;
    while(size--)
        *p++ = c;
    return buf;
}

#define memmove memcpy
char *memcpy(char *dest, char *src, size_t n) {
    for(int i = 0; i < n; i++)
        dest[i] = src[i];
    return dest;
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

bool strcmp(char *s1, char *s2) {
    if(strlen(s1) != strlen(s2))
        return false;
    
    for(int i = 0; s1[i] != '\0'; i++)
        if(s1[i] != s2[i])
            return false;
    
    return true;
}

void gets(char *buf, int size) {
    int i, c;
    for(i = 0; i < (size - 1) && (c = getc()) != '\n'; i++) {
        if(c != '\b') {
            buf[i] = c;
            putc(buf[i]);
        } else if(i > 0) {
            i -= 2;
            printf("\b \b");
        }
    }
    printf("\n");
    buf[i] = '\0';
}

int __alloca_stack[250000];
int __alloca_stackptr = 0;
void *alloca(size_t size) {
    if(__alloca_stackptr + size >= sizeof(__alloca_stack))
        __alloca_stackptr = 0;
    
    void *p = &__alloca_stack[__alloca_stackptr];
    __alloca_stackptr += size;
    return p;
}


#endif
#endif
