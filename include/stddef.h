/* --Menshikov S. */

#ifndef _STDDEF_H
#define _STDDEF_H    1

typedef int size_t;
typedef int ptrdiff_t;

#define offsetof(t, m) ((size_t)&(((t *)0)->m))

#define NULL ((void *)0)

#endif
