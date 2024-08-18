#ifndef __malloc_h

#include "useful.h"

#define MALLOC_BLK_SIZE      10000
bool __malloc_mem_table[30] = {
    false, false, false, false, false,    /* false = свободен, true = занят */
    false, false, false, false, false,
    false, false, false, false, false,
    false, false, false, false, false,
    false, false, false, false, false,
    false, false, false, false, false,
};

#define MALLOC_LARGEBLK_SIZE      100000
bool __malloc_largemem_table[5] = {false, false, false, false, false};

char __malloc_mem[MALLOC_BLK_SIZE * 30];
char __malloc_largemem[MALLOC_LARGEBLK_SIZE * 5];


/* поиск первого свободного блока */

int __malloc_search_free_blk() {
    int i;
    for(i = 0; i < sizeof(__malloc_mem_table); i++)
        if(!__malloc_mem_table[i])
            break;
    
    return (i < sizeof(__malloc_mem_table) ? i : -1);
}

int __malloc_search_free_largeblk() {
    int i;
    for(i = 0; i < sizeof(__malloc_largemem_table); i++)
        if(!__malloc_largemem_table[i])
            break;
    
    return (i < sizeof(__malloc_largemem_table) ? i : -1);
}

/**********************************/

void *malloc(size_t size) {
    if(size <= 0 || size >= MALLOC_LARGEBLK_SIZE)
        return NULL;
    else if(size > 0 && size < MALLOC_BLK_SIZE) {
        int free_blk = __malloc_search_free_blk();
        if(free_blk == -1)
            return NULL;
        
        void *ptr = &__malloc_mem[MALLOC_BLK_SIZE * free_blk];
        __malloc_mem_table[free_blk] = true;
        
        return ptr;
    } else if(size >= MALLOC_BLK_SIZE && size < MALLOC_LARGEBLK_SIZE) {
        int free_blk = __malloc_search_free_largeblk();
        if(free_blk == -1)
            return NULL;
        
        void *ptr = &__malloc_largemem[MALLOC_LARGEBLK_SIZE * free_blk];
        __malloc_largemem_table[free_blk] = true;
        
        return ptr;
    }
}

void free(void *ptr) {
    if(ptr == NULL)
        return;
    else if(ptr >= &__malloc_mem[0] && ptr <= &__malloc_mem[sizeof(__malloc_mem) - 1])
        __malloc_mem_table[(ptr - &__malloc_mem[0]) / MALLOC_BLK_SIZE] = false;
    else if(ptr >= &__malloc_largemem[0] && ptr <= &__malloc_largemem[sizeof(__malloc_largemem) - 1])
        __malloc_largemem_table[(ptr - &__malloc_largemem[0]) / MALLOC_LARGEBLK_SIZE] = false;
}

void *calloc(size_t n, size_t size) {
    void *ptr = malloc(n * size);
    if(ptr == NULL)
        return NULL;
    
    memset(ptr, '\0', n * size);
    
    return ptr;
}

void *realloc(void *ptr, size_t new_size) {
    if(ptr == NULL)
        return malloc(new_size);
    else if(new_size >= MALLOC_LARGEBLK_SIZE)
        return NULL;
    else if(new_size >= MALLOC_BLK_SIZE && ptr >= &__malloc_mem && ptr <= &__malloc_mem[sizeof(__malloc_mem) - 1]) {
        void *new_p = malloc(new_size);
        if(new_p == NULL)
            return NULL;
        
        for(int i = 0; i < MALLOC_BLK_SIZE; i++)
            new_p[i] = ptr[i];
        
        return new_p;
    } else
        return ptr;
}

#endif
