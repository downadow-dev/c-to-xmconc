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

int comm_delay = 60;   /* вы можете изменить это в своей программе */

int *comm(int *msg, int n) {
    if(msg != NULL) {
        if(n == 0) n = strlen(msg) + 1;
        
        for(int i = 0; i < n; i++)
            mem[9999000 + i] = msg[i];
        
        msleep(comm_delay);
    }
    
    return (int *)9999872;
}


#endif
#endif
