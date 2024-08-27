#ifndef ___get_args_h
#ifdef __XCC_C__

#define ___get_args_h   1

int ___get_args(char ***argv_ptr) {
    static char args[128];
    getargs(args);
    
    static char *argv[32];
    int argc = (args[0] == '\0' ? 1 : 2);
    argv[0] = "<prog>";
    argv[1] = &args[0];
    
    int args_length = strlen(args);
    for(int i = 0; i < args_length; i++) {
        if(args[i] == ' ') {
            args[i] = '\0';
            argv[argc] = &args[i + 1];
            argc++;
        } else if(args[i] == '\r')
            args[i] = ' ';
    }
    
    *(argv_ptr) = &argv[0];
    
    return argc;
}

#endif
#endif

