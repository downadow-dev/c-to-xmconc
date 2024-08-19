int array[2][16];

int main() {
    for(int i = 0; i < 16; i++) {
        array[0][i] = i + 1;
        array[1][i] = -(i + 1);
        
        printf("%d\t%d\n", array[0][i], array[1][i]);
    }
}
