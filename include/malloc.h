#ifndef __malloc_h
#define __malloc_h   1

#include <misc.h>

#define MALLOC_MEM    450000
char __malloc_mem  [MALLOC_MEM];
char __malloc_sizes[MALLOC_MEM];

bool __malloc_need_init = true;

void __malloc_init(void) {
    /* инициализация данных */
    memset(__malloc_sizes, '\0', MALLOC_MEM);
    
    __malloc_need_init = false;
}

/* malloc(): выделение памяти */
char *malloc(size_t size) {
    if(__malloc_need_init) __malloc_init();
    
    /* поиск первого свободного блока */
    
    for(int i = 0; i < MALLOC_MEM; i++) {
        /* занятый блок; игнорируем */
        if(__malloc_sizes[i] > 0) {
            i += __malloc_sizes[i] - 1;
            continue;
        }
        /* занимаем свободный блок */
        else if(__malloc_sizes[i] < 0 && -(__malloc_sizes[i]) >= size) {
            __malloc_sizes[i] = size;
            return &__malloc_mem[i];
        }
        /* здесь может быть свободный блок */
        else if(__malloc_sizes[i] <= 0) {
            int j;
            for(j = i; j < MALLOC_MEM && __malloc_sizes[j] <= 0; j++) {
                if(j-i+1 >= size) {
                    __malloc_sizes[i] = size;
                    return &__malloc_mem[i];
                }
            }
            
            i = j+1;
        }
    }
    
    /**********************************/
    
    return NULL;
}

/* free(): освобождение */
void free(char *p) {
    __malloc_sizes[p - __malloc_mem] = -(__malloc_sizes[p - __malloc_mem]);
}

/* calloc(): "чистое" выделение */
char *calloc(size_t n, size_t size) {
    char *p = malloc(n * size);
    if(p == NULL) return NULL;
    
    memset(p, '\0', n * size);
    
    return p;
}

char *realloc(char *p, size_t new_size) {
    if(p == NULL)
        return malloc(new_size);
    
    /********************************/
    
    char *new_p = malloc(new_size);
    if(new_p == NULL) return NULL;
    
    memcpy(new_p, p, __malloc_sizes[p - __malloc_mem]);
    free(p);
    
    return new_p;
}


#endif
