#ifndef _STDIO_H
#define _STDIO_H    1

#include <stdarg.h>
#include <stdlib.h>
#include <string.h>

#define EOF          (-1)

int getchar(void) {
    char c;
    for(;;) {
        c = _call("getc");
        if(c != 0 && c != 65535)
            break;
    }
    
    return (c != 4 /* Ctrl+D */ && c != 3 /* Ctrl+C */) ? c : EOF;
}

int putchar(int c) {
    switch(c) {
        case '\n':
            _call("newline");
            break;
        case '\b':
            _call("backspace");
            break;
        case '\r':
            _call("cr");
            break;
        default:
            _call("putc", c);
    }
    return c;
}

/* put number to string */

char *_sprinti(long long v, char *start, int base, int upper) {
    if(v < 0) {
        v = -v;
        *start++ = '-';
    }
    
    if(v / base) start = _sprinti(v / base, start, base, upper);
    *start++ = (v % base) < 10 ? ((v % base) + '0') : ((v % base) - 10 + (upper ? 'A' : 'a'));
    return start;
}

/* vsprintf */
int vsprintf(char *s, char *fmt, va_list ap) {
    int n = 0;
    char *p;
    char *orig = s;
    
    while(*fmt) {
        if(*fmt == '%') {
            fmt++;
            
            while(*fmt == 'l' || *fmt == 'h' || *fmt == 't' || *fmt == 'z' || *fmt == 'j' || *fmt == ' ')
                fmt++;
            
            switch(*fmt) {
                case '%':
                    *s++ = '%';
                    break;
                case 'i':
                case 'd':
                case 'u':
                    s = _sprinti(va_arg(ap, int), s, 10, 0);
                    break;
                case 'p':
                    p = va_arg(ap, void *);
                    if(p) {
                        *s++ = '0';
                        *s++ = 'x';
                        s = _sprinti(p, s, 16, 0);
                    } else {
                        s = stpcpy(s, "(nil)");
                    }
                    break;
                case 'x':
                    s = _sprinti(va_arg(ap, int), s, 16, 0);
                    break;
                case 'X':
                    s = _sprinti(va_arg(ap, int), s, 16, 1);
                    break;
                case 'o':
                    s = _sprinti(va_arg(ap, int), s, 8, 0);
                    break;
                case 'c':
                    *s = (char)va_arg(ap, int);
                    if(*s) s++;
                    break;
                case 's':
                    p = va_arg(ap, char *);
                    s = stpcpy(s, p ? p : "(null)");
                    break;
                default:
                    return -1;
            }
        } else *s++ = *fmt;
        
        fmt++, n++;
        
        if(s - orig > 2000)
            break;
    }
    
    *s = '\0';
    
    return n;
}


/* vprintf */
int vprintf(char *fmt, va_list ap) {
    int n;
    static char buf[2048];
    
    n = vsprintf(buf, fmt, ap);
    if(n != -1) {
        for(char *p = buf; *p; p++) {
            putchar(*p);
        }
    }
    
    return n;
}

/* sprintf */
int sprintf(char *s, char *fmt, ...) {
    int n;
    va_list ap;
    
    va_start(ap, fmt);
    n = vsprintf(s, fmt, ap);
    va_end(ap);
    
    return n;
}

int printf(char *fmt, ...) {
    int n;
    va_list ap;
    
    va_start(ap, fmt);
    n = vprintf(fmt, ap);
    va_end(ap);
    
    return n;
}

#define puts(s)  printf("%s\n", (s))

char *gets(char *buf, int size) {
    int i, c;
    for(i = 0; i < (size - 1) && (c = getchar()) != '\n'; i++) {
        if(c == EOF) {
            buf[i] = '\0';
            return NULL;
        } else if(c != '\b') {
            buf[i] = c;
            printf("%c█\b", buf[i]);
        } else if(i > 0) {
            i -= 2;
            printf(" \b\b█\b");
        }
    }
    printf(" \n");
    buf[i] = '\0';
    
    return buf;
}

#endif
