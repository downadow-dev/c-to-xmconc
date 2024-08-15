#define true   1
#define false  0

typedef void __thrd1_t;


__thrd1_t a() {
    for(static int i = 0; true; i++) {
        printf("%d: thread 1\n", i);
        msleep(1400);
    }
}

int main() {
    a();
    
    for(int i = 0; true; i++) {
        printf("%d: thread 0\n", i);
        sleep(1);
    }
}
