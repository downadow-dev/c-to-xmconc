#ifndef __malloc_h
#define __malloc_h   1


#include "useful.h"

int __malloc_mem[900000];
int __malloc_ptr = 1;

int __last_free_ptr = -1;

char *malloc(size_t size) {
    char *ptr;
    
    if(__last_free_ptr > -1 && size <= __malloc_mem[__last_free_ptr - 1]) {
        ptr = __last_free_ptr;
        __last_free_ptr = -1;
        return ptr;
    }
    
    if((__malloc_ptr + size) >= sizeof(__malloc_mem))
        __malloc_ptr = 100000;
    
    __malloc_mem[__malloc_ptr - 1] = size;
    ptr = &__malloc_mem[__malloc_ptr];
    __malloc_ptr += size + 1;
    
    return ptr;
}

char free(char *ptr) {
    if(ptr != NULL)
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
    char *new_p = malloc(size);
    for(int i = 0; i < *(ptr - 1); i++)
        new_p[i] = ptr[i];
    free(ptr);
    return new_p;
}


#endif
