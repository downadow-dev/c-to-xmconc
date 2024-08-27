#ifndef __xmtwolime_h
#ifdef __XCC_C__

#define __xmtwolime_h     1


int *mem = (int *) 0;

/* какие-то константы */
#define USERSPACE_START   8700000
#define USERSPACE_END     9999999
#define MEM_START         6900000

#define UID_USER          1
#define UID_ROOT          0
/**********************/

#ifndef NULL
#define NULL              ((void *) 0)
#endif


#endif
#endif
