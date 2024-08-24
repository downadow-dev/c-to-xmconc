/* for Xmtwolime */


#include <useful.h>
#include <xmtwolime.h>

int main() {
    char buf[128];
    getargs(buf);
    
    if((getuid() != UID_ROOT && atoi(buf) >= USERSPACE_START) || getuid() == UID_ROOT)
        printf("%d\n", mem[atoi(buf)]);
    else {
        printf("root required\n");
        exit(EXIT_FAILURE);
    }
}

