#ifndef __stdarg_h
#define __stdarg_h   1

typedef int va_list;

#define va_start(l, last)    ((l) = 0)
#define va_arg(l, t)         (*((t)(&___vargs)+(l++)))
#define va_end(l)
#define va_copy(dst, src)    ((dst) = (src))

#endif

