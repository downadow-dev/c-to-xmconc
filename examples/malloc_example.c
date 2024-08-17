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
    char buf[16];
    
    printf("Enter a size of new array: ");
    gets(buf, sizeof(buf));
    int len = atoi(buf);
    char *a = xalloc(len);
    
    memset(a, '\0', len);
    
    int i;
    for(i = 0; i < len; i++) {
        printf("Enter a value for a[%d]: ", i);
        memset(buf, '\0', sizeof(buf));
        gets(buf, sizeof(buf));
        a[i] = atoi(buf);
    }
    
    printf("\nAddress of a: %u\nValues:  %d", a, a[0]);
    for(int j = 1; j < i; j++)
        printf(", %d", a[j]);
    printf("\n");
}
