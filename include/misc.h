#ifndef __misc_h
#define __misc_h    1


#define true         1
#define false        0
typedef int bool;

#define EOT          4   /* Ctrl+D */

typedef long size_t;
typedef long ssize_t;
typedef void __thread1_t;

#define NULL         ((void *) 0)

#define putchar(c)   putc(c)
#define getchar()    getc()

#define thrd1_char   static char
#define thrd1_int    static int

#define EXIT_SUCCESS 0
#define EXIT_FAILURE 1


#endif

