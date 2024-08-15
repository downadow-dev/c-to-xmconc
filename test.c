#define meminit(buf, size)   for(int i = 0; i < size; i++) buf[i] = '\0';

int atoi(char *s) {
    char s2[8];
    meminit(s2, sizeof(s2));
    
    int j;
    if(s[0] == '-' || s[0] == '+')
        j = 1;
    else
        j = 0;
    for(int i = (sizeof(s2) - strlen(s) - 1); i < (sizeof(s2) - 1); i++)
        s2[i] = s[j++] - (int)'0';
    
    int num = cat(s2[1], s2[2], s2[3], s2[4],
        s2[5], s2[6]) + (1000000 * s2[0]);
    
    if(s[0] == '-')
        num = -num;
    
    return num;
}

int main() {
    char buf[128];
    getargs(buf);
    
    printf("%d\n", atoi(buf) + atoi(buf));
}

