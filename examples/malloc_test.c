#include "simple_malloc.h"

int main() {
    char *a = malloc(100);
    char *b = malloc(10000);
    char *c = malloc(8);
    char *d = malloc(90);
    
    printf("a\tb\tc\td\n");
    printf("%u\t%u\t%u\t%u\n", a, b, c, d);
    
    a = realloc(a, 160);
    c = realloc(c, 90000);
    
    printf("a\tb\tc\td\n");
    printf("%u\t%u\t%u\t%u\n", a, b, c, d);
    
    free(a);
    a = NULL;
    
    int *e = calloc(512, sizeof(int));
    
    printf("b\tc\td\te\n");
    printf("%u\t%u\t%u\t%u\n", b, c, d, e);
}

