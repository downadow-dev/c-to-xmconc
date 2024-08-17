#ifndef __useful_h
#define __useful_h   1

#define true         1
#define false        0
typedef int bool;

typedef long size_t;

#define NULL         (void *) 0

#define memset(buf, c, size)   for(int i = 0; i < size; i++) buf[i] = c;

int atoi(char *s) {
    char s2[8];
    memset(s2, '\0', sizeof(s2));
    
    int j;
    if(s[0] == '-' || s[0] == '+')
        j = 1;
    else
        j = 0;
    for(int i = (sizeof(s2) - strlen(s) - 1); i < (sizeof(s2) - 1); i++)
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


#endif
