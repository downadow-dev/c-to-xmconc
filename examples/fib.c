
int fib(int n) {
    if(n == 0 || n == 1)
        return n;
    else
        return fib(n - 1) + fib(n - 2);
}

int main() {
    for(int i = 0; i < 21; i++)
        printf("%d\n", fib(i));
    
}

