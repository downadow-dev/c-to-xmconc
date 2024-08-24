
typedef void __thread1_t;  /* тип должен начинаться с ``__thr`` */

int counter_active;

__thread1_t counter() {
    counter_active = 1;
    
    static int i;
    for(i = 0; counter_active; i++) {
        printf("\r%d", i);
        sleep(1);
    }
    
    halt();
}

int main() {
    counter();
    
    getc();
    
    counter_active = 0;
    sleep(1);
    exit(0);
}

