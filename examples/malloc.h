#ifndef __malloc_h
#define __malloc_h   1


#include "useful.h"

#ifndef MALLOC_BLK_SIZE
# define MALLOC_BLK_SIZE    30000
#endif

int __malloc_mem[MALLOC_BLK_SIZE * 28];
int __malloc_ptr = 0;

int __last_free_ptr = -1;

char *malloc(size_t size) {
    char *ptr;
    
    if(__last_free_ptr > -1) {
        ptr = __last_free_ptr;
        __last_free_ptr = -1;
        return ptr;
    }
    
    if((__malloc_ptr + size) >= sizeof(__malloc_mem))
        return NULL;
    
    ptr = &__malloc_mem[__malloc_ptr];
    __malloc_ptr += (size / MALLOC_BLK_SIZE + 1) * MALLOC_BLK_SIZE;
    
    return ptr;
}

char free(char *ptr) {
    __last_free_ptr = ptr;
}

char *calloc(size_t n, size_t size) {
    char *ptr = malloc(n * size);
    
    if(ptr == NULL)
        return NULL;
    
    memset(ptr, '\0', n * size);
    
    return ptr;
}

char *realloc(char *ptr, size_t size) {
    return size < MALLOC_BLK_SIZE ? ptr : NULL;
}


#endif
