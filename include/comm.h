#ifndef __comm_h
#ifdef __XCC_C__

#define __comm_h     1

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
