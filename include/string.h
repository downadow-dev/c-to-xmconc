#ifndef _STRING_H
#define _STRING_H    1

#include <stddef.h>

char *strchr(char *s, int c) {
    if(c == '\0')
        return s+strlen(s);
    else {
        char *p = s;
        while(*p && *p != c) p++;
        return *p ? p : NULL;
    }
}

char *strrchr(char *s, int c) {
    char *prev = NULL;
    char *p = s;
    
    while(p = strchr(p, c))
        prev = p++;
    
    return prev;
}

size_t strnlen(char *s, size_t max) {
    for(int i = 0; i < max; i++) {
        if(s[i] == '\0')
            return i;
    }
    
    return max;
}

char *memchr(char *m, char c, size_t n) {
    for(int i = 0; i < n; i++) {
        if(m[i] == c)
            return &m[i];
    }
    return NULL;
}

int memcmp(char *m1, char *m2, size_t n) {
    for(int i = 0; i < n; i++) {
        if(m1[i] != m2[i])
            return m1[i] - m2[i];
    }
    return 0;
}

char *memmove(char *dst, char *src, size_t n) {
    if(dst < src)
        return memcpy(dst, src, n);
    else if(dst != src) {
        for(int i = n-1; i >= 0; i--)
            dst[i] = src[i];
    }
    return dst;
}

int strcmp(char *s1, char *s2) {
    for(int i = 0; s1[i] || s2[i]; i++) {
        if(s1[i] != s2[i])
            return s1[i] - s2[i];
    }
    return 0;
}

int strncmp(char *s1, char *s2, size_t n) {
    for(int i = 0; i < n && (s1[i] || s2[i]); i++) {
        if(s1[i] != s2[i])
            return s1[i] - s2[i];
    }
    return 0;
}

char *strstr(char *s, char *ss) {
    size_t sslen = strlen(ss);
    while(*s) {
        if(*s == *ss) {
            if(strlen(s) >= sslen) {
                if(memcmp(s, ss, sslen) == 0)
                    return s;
            } else return NULL;
        }
        s++;
    }
    return NULL;
}

/* no strtok */

char *strsep(char **sp, char *d) {
    char *saved = *sp;
    if(saved == NULL)
        return NULL;
    for(int i = 0; saved[i]; i++) {
        for(int j = 0; d[j]; j++) {
            if(saved[i] == d[j]) {
                saved[i] = '\0';
                *sp = &saved[i+1];
                return saved;
            }
        }
    }
    *sp = NULL;
    return saved;
}

char *mempcpy(char *dst, char *src, size_t n) {
    memcpy(dst, src, n);
    return dst + n;
}

char *strcpy(char *dst, char *src) {
    return memcpy(dst, src, strlen(src) + 1);
}

char *stpcpy(char *dst, char *src) {
    return mempcpy(dst, src, strlen(src) + 1) - 1;
}

char *strcat(char *dst, char *src) {
    memcpy(dst + strlen(dst), src, strlen(src) + 1);
    return dst;
}

char *strncpy(char *dst, char *src, size_t n) {
    *(mempcpy(dst, src, strnlen(src, n))) = '\0';
    return dst;
}

char *strncat(char *dst, char *src, size_t n) {
    *(mempcpy(dst + strlen(dst), src, strnlen(src, n))) = '\0';
    return dst;
}

char *strpbrk(char *s, char *ac) {
    while(*s) {
        for(char *p = ac; *p; p++) {
            if(*s == *p) return s;
        }
        s++;
    }
    
    return NULL;
}

size_t strspn(char *s, char *ac) {
    size_t len = 0;
    while(*s) {
        for(char *p = ac; *p; p++) {
            if(*s == *p) goto next;
        }
        return len;
        next: s++, len++;
    }
    return len;
}

size_t strcspn(char *s, char *rj) {
    size_t len = 0;
    while(*s) {
        for(char *p = rj; *p; p++) {
            if(*s == *p) return len;
        }
        s++, len++;
    }
    return len;
}

#endif
