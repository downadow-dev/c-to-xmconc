/* --Menshikov S. */

#ifndef __stdarg_h
#define __stdarg_h   1

typedef char * va_list;

#define va_start(l, last)    ((l) = &___vargs)
#define va_arg(l, t)         ((t)(*((l)++)))
#define va_end(l)
#define va_copy(dst, src)    ((dst) = (src))

#endif

