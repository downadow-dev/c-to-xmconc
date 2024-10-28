/* --Menshikov S. */

#ifndef _STDDEF_H
#define _STDDEF_H    1

typedef unsigned long size_t;
typedef long ssize_t;
typedef long ptrdiff_t;
typedef int wchar_t;
typedef int wint_t;

#define offsetof(t, m) ((size_t)&(((t *)0)->m))

#define NULL ((void *)0)

#endif
