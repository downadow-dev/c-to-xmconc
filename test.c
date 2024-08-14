#define meminit(a, s)   for(int i = 0; i < s; i++) a[i] = '\0';

int get_num() {
    char array[8];
    meminit(array, sizeof(array));
    
    int c;
    for(int i = 0; (c = getc()) != '\n' && i < (sizeof(array) - 1); i++) {
        array[i] = c - (int)'0';
        putc(c);
    }
    printf("\n");
    
    char new_array[8];
    meminit(new_array, sizeof(new_array));
    
    int j = 0;
    for(int i = (sizeof(array) - strlen(&array) - 1); i < (sizeof(new_array) - 1); i++)
        new_array[i] = array[j++];
    
    return cat(new_array[6], new_array[5], new_array[4], new_array[3],
        new_array[2], new_array[1]) + (1000000 * new_array[0]);
}

int main() {
    printf("%d\n", get_num());
}

