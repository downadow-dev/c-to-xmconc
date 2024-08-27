#include <useful.h>

char block = '@';
char map[1024];
#define WIDTH     41

int p = 0;

void move(int n, int c) {
    if(map[p + n] == '.') {
        map[p + n] = '+';
        map[p] = c;
        p += n;
    }
}

void boom() {
    if(map[p + WIDTH] == block) map[p + WIDTH] = '.';
    if(map[p - WIDTH] == block) map[p - WIDTH] = '.';
    if(map[p + 1] == block)     map[p + 1] = '.';
    if(map[p - 1] == block)     map[p - 1] = '.';
}

int main() {
    char *new_map = "\
+....................................... \
........................................ \
........................................ \
........................................ \
........................................ \
........................................ \
........................................ \
........................................ \
........................................ \
........................................ \
........................................ \
........................................ \
........................................ \
........................................ \
........................................ \
........................................ \
........................................ \
........................................ \
........................................";
    
    memcpy(map, new_map, strlen(new_map) + 1);
    int map_length = strlen(map);
    
    while(true) {
        /* вывод карты */
        clear_output();
        for(int i = 0; i < map_length; i++) {
            if(map[i] == ' ')
                printf("\n");
            else
                putchar(map[i]);
        }
        /***************/
        
        int c = getchar();
        
        switch(c) {
            case 'w': move(-WIDTH, '.'); break;
            case 's': move(WIDTH, '.'); break;
            case 'a': move(-1, '.'); break;
            case 'd': move(1, '.'); break;
            
            case 'W': move(-WIDTH, block); break;
            case 'S': move(WIDTH, block); break;
            case 'A': move(-1, block); break;
            case 'D': move(1, block); break;
            
            case ' ': boom(); break;
            
            case 033: exit(EXIT_SUCCESS); break;
            
            default: if(c < 127) block = c;
        }
    }
}
