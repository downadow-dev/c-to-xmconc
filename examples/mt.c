
typedef void __thread1_t;  /* тип должен начинаться с ``__thr`` */

int counter_active;

__thread1_t counter() {
    counter_active = 1;
    
    for(static int i = 0; counter_active; i++) {
        printf("%d", i);
        
        if(i < 10)        printf("\b");
        else if(i < 100)  printf("\b\b");
        else              printf("\b\b\b");
        
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

