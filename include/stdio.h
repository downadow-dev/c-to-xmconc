#ifndef _STDIO_H
#define _STDIO_H    1

#include <stdarg.h>
#include <stdlib.h>

#define EOF          (-1)

int getchar(void) {
    char c = _call("getc");
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

void _printi(int v, int base, int upper) {
    if(v < 0) {
        v = -v;
        putchar('-');
    }
    
    if(v / base) _printi(v / base, base, upper);
    putchar((v % base) < 10 ? ((v % base) + '0') : ((v % base) - 10 + (upper ? 'A' : 'a')));
}

int vprintf(char *fmt, va_list ap) {
    int n = 0;
    char *p;
    
    while(*fmt) {
        if(*fmt == '%') {
            fmt++;
            
            while(*fmt == 'l' || *fmt == 'h' || *fmt == 't' || *fmt == 'z' || *fmt == 'j' || *fmt == ' ')
                fmt++;
            
            switch(*fmt) {
                case '%':
                    putchar('%');
                    break;
                case 'i':
                case 'd':
                case 'u':
                    _printi(va_arg(ap, int), 10, 0);
                    break;
                case 'p':
                    p = va_arg(ap, void *);
                    if(p) {
                        _call("puts", "0x");
                        _printi(p, 16, 0);
                    } else {
                        _call("puts", "(nil)");
                    }
                    break;
                case 'x':
                    _printi(va_arg(ap, int), 16, 0);
                    break;
                case 'X':
                    _printi(va_arg(ap, int), 16, 1);
                    break;
                case 'o':
                    _printi(va_arg(ap, int), 8, 0);
                    break;
                case 'c':
                    putchar(va_arg(ap, char));
                    break;
                case 's':
                    p = va_arg(ap, char *);
                    _call("puts", p ? p : "(null)");
                    break;
                default:
                    return -1;
            }
        } else putchar(*fmt);
        
        fmt++, n++;
    }
    
    return n;
}

#ifndef _DEFAULT_PRINTF
int printf(char *fmt, ...) {
    int n;
    va_list ap;
    
    va_start(ap, fmt);
    n = vprintf(fmt, ap);
    va_end(ap);
    
    return n;
}
#endif

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
