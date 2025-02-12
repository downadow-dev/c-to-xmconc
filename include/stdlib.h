#ifndef _STDLIB_H
#define _STDLIB_H   1

/* codes for exit() */
#define EXIT_SUCCESS   0
#define EXIT_FAILURE   1
/********************/
#define abort()        exit(-1)

#include <ctype.h>
#include <stddef.h>

/* strtol */

int _strtol_digit(int c) {
    if(isdigit(c))
        return c - '0';
    else if(isalpha(c))
        return tolower(c) - 'a' + 10;
    else
        return -1;
}

#define strtoll   strtol
int strtol(char *s, char **end, int base) {
    int num = 0, negative = 0;
    
    /* skip first spaces */
    while(isspace(*s))
        s++;
    
    /* checking for optional +/- */
    switch(*s) {
    case '-':
        negative = 1;   /* and fall through */
    case '+':
        s++;
    }
    /********************/
    if(s[0] == '0' && (s[1] == 'x' || s[1] == 'X')) {
        s += 2;
        base = 16;
    } else if(*s == '0' && base == 0) {
        s++;
        base = 8;
    } else if(base == 0)
        base = 10;
    /********************/
    while(*s == '0')
        s++;
    
    while(isalnum(*s))
        s++;
    if(end) *end = s;
    s--;
    
    int n = 1;
    while(isalnum(*s) && *s != 'x' && *s != 'X') {
        num += n * _strtol_digit(*s);
        n *= base;
        s--;
    }
    
    return negative ? -num : num;
}

/* atoi */

#define atol   atoi
#define atoll  atoi
int atoi(char *s) {
    int num = 0, negative = 0;
    
    while(isspace(*s))
        s++;
    
    switch(*s) {
    case '-':
        negative = 1;   /* and fall through */
    case '+':
        s++;
    }
    
    while(*s == '0')
        s++;
    
    while(isdigit(*s))
        s++;
    s--;
    
    int n = 1;
    while(isdigit(*s)) {
        num += n * (*s - '0');
        n *= 10;
        s--;
    }
    
    return negative ? -num : num;
}

#endif
