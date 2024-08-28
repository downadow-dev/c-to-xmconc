#ifndef __assert_h
#define __assert_h     1

#ifdef NDEBUG
# define assert(expr)
#else
# define assert(expr)    if(!(expr)) { printf("%s:%d: %s: assert(%s) failed\n", __FILE__, __LINE__, __func__, #expr); exit(-1); }
#endif

#endif
