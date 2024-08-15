#define WIDTH   32
#define HEIGHT  15

struct coord {
    int x;
    int y;
};


void print_map(struct coord *c) {
    for(int i = 0; i < HEIGHT; i++) {
        for(int j = 0; j < WIDTH; j++) {
            if(i == c->y && j == c->x)
                putc('%');
            else
                putc('.');
        }
        printf("\n");
    }
}

int main() {
    struct coord crd = {4, 9};
    print_map(&crd);
}

