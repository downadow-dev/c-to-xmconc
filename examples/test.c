int main() {
    char *a[2];
    char buf1[64];
    char buf2[64];
    
    a[0] = &buf1[0];
    a[1] = &buf2[0];
    
    for(int i = 0; i < 64; i++) {
        a[0][i] = i;
        a[1][i] = -i;
        
        printf("%d\t%d\n", a[0][i], a[1][i]);
    }
}
