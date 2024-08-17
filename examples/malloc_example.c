#include "malloc.h"

char *xalloc(size_t size) {
    char *ptr = malloc(size);
    
    if(ptr == NULL) {
        printf("*** error: malloc() returned NULL\n");
        exit(1);
    }
    
    return ptr;
}

int main() {
    char *a = xalloc(64);
    char *b = xalloc(64);
    char *c = xalloc(64);
    
    printf("before free(b):\n");
    printf("\n");
    
    printf("\ta:\t%u\n", a);
    printf("\tb:\t%u\n", b);
    printf("\tc:\t%u\n", c);
    
    free(b);
    
    char *d = xalloc(64);
    char *e = xalloc(64);
    
    printf("\n");
    printf("after free(b):\n");
    printf("\n");
    
    printf("\ta:\t%u\n", a);
    printf("\tc:\t%u\n", c);
    printf("\td:\t%u\n", d);
    printf("\te:\t%u\n", e);
}
