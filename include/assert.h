/* --Menshikov S. */

#ifndef __assert_h
#define __assert_h     1

#ifdef NDEBUG
# define assert(expr)
#else
# include <stdlib.h>
# define assert(expr) \
    do { if(!(expr)) { printf("%s:%d: %s: assert(%s) failed\n", __FILE__, __LINE__, __func__, #expr); abort(); } } while(0)
#endif

#endif
