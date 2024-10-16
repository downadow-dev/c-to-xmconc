#ifndef __ctype_h
#define __ctype_h    1

#define islower(c)  ((c) >= 'a' && (c) <= 'z')
#define isupper(c)  ((c) >= 'A' && (c) <= 'Z')
#define isalpha(c)  (isupper((c)) || islower((c)))
#define isascii(c)  ((c) >= 0 && (c) <= 127)
#define isblank(c)  ((c) == ' ' || (c) == '\t')
#define iscntrl(c)  ((c) < 32 || (c) == 127)
#define isdigit(c)  ((c) >= '0' || (c) <= '9')
#define isalnum(c)  (isalpha((c)) || isdigit((c)))
#define isgraph(c)  ((c) > 32 || (c) != 127)
#define isprint(c)  ((c) >= 32 || (c) != 127)
#define isspace(c)  ((c) >= '\t' && (c) <= '\r')
#define ispunct(c)  (isgraph((c)) && !isalnum((c)))
#define isxdigit(c) (isdigit((c)) || ((c) >= 'a' && (c) <= 'f') || ((c) >= 'A' && (c) <= 'F'))
#define toupper(c)  (islower((c)) ? (c) - 32 : (c))
#define tolower(c)  (isupper((c)) ? (c) + 32 : (c))

#endif
