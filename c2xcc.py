#!/usr/bin/python3

from pycparser.c_ast import *


current_function = ''   # мы находимся в теле этой функции
                        # (пока лишь в глобальном пространстве имён)

variables = []          # переменные
functions = []          # функции

funcfixed = {}

continuel = 0
current_if = 0
current_for = 0
current_while = 0
current_switchl = 0
current_continue = ''
current_break = ''

enumerators = {}
structs = {}
structures = {}
structuresnoptrs = {}
unions = {}
unionlist = {}

typedef_structs = []
typedef_unions = []

def reset():
    global continuel
    continuel = 0
    global variables
    variables = []
    global functions
    functions = []
    global funcfixed
    funcfixed = {}
    global current_function
    current_function = ''
    global current_string
    current_string = 0
    global current_if
    current_if = 0
    global current_for
    current_for = 0
    global current_while
    current_while = 0
    global current_switchl
    current_switchl = 0
    global enumerators
    enumerators = {}
    global structures
    structures = {}
    global structuresnoptrs
    structuresnoptrs = {}
    global structs
    structs = {}
    global unionlist
    unionlist = {}
    global unions
    unions = {}
    global typedef_structs
    typedef_structs = []
    global typedef_unions
    typedef_unions = []
    global current_continue
    current_continue = ''
    global current_break
    current_break = ''

# получить переменную/массив
def get_var(name):
    if ('___F___' + name) in variables:
        return '{___F___' + name + '}'
    elif current_function == '' or not (current_function + '.' + name) in variables:
        return '{' + name + '}'
    else:
        return '{' + current_function + '.' + name + '}'

# создаёт переменную/массив
def create_var(name, array_len=0):
    global variables
    
    if current_function != '':
        name = current_function + '.' + name
    
    if not name in variables:
        variables += [name]
    return '/alloc ' + name + ('[' + str(array_len) + ']' if array_len > 0 else '') + '\n'

# преобразовать '\'-последовательности в строке
def preprocess_string(s):
    # пропустить префиксы вроде L
    while not s.startswith('"') and not s.startswith("'"):
        s = s[1:]
    
    return s[1:-1].replace('\\\\', '%/\\\\/%')  \
        .replace('\\"', '"')                    \
        .replace('\\\'', '\'')                  \
        .replace('\\n', '\n')                   \
        .replace('\\b', '\b')                   \
        .replace('\\r', '\r')                   \
        .replace('\\t', '\t')                   \
        .replace('\\f', '\f')                   \
        .replace('\\a', '\a')                   \
        .replace('\\v', '\v')                   \
        .replace('\\033', '\033')               \
        .replace('\\0', '\0')                   \
        .replace('%/\\\\/%', '\\')

# код в начале программы
def get_init_code():
    return '''
/alloc ___ret[64]
/alloc __retptr
0 {__retptr} =
/define function :({___ret} {__retptr}! +) = ({__retptr}! ++) {__retptr} =
/define return :({__retptr}! --) {__retptr} = (({___ret} {__retptr}! +) .) goto
'''

# "2 == 4" => "2 4 =?" и т. д.
def compile_cond(op):
    if op == None:
        return '1' # true
    elif type(op) == UnaryOp and op.op == '!':
        return compile_cond(op.expr) + ' !'
    
    if type(op) == BinaryOp:
        if op.op == '==':
            return compile_obj(op.left) + ' ' + compile_obj(op.right) + ' =?'
        elif op.op == '!=':
            return compile_obj(op.left) + ' ' + compile_obj(op.right) + ' !?'
        elif op.op == '<':
            return compile_obj(op.left) + ' ' + compile_obj(op.right) + ' lt?'
        elif op.op == '>':
            return compile_obj(op.left) + ' ' + compile_obj(op.right) + ' gt?'
        elif op.op == '>=':
            return compile_obj(op.left) + ' ' + compile_obj(op.right) + ' -- gt?'
        elif op.op == '<=':
            return compile_obj(op.left) + ' ' + compile_obj(op.right) + ' ++ lt?'
        
        elif op.op == '&&':
            return compile_cond(op.left) + ' ' + compile_cond(op.right) + ' ?'
        elif op.op == '||':
            return compile_cond(op.left) + ' ' + compile_cond(op.right) + ' |?'
        
        else:
            return compile_obj(op) + ' 0 !?'
    
    else:
        return compile_obj(op) + ' 0 !?'


def static_int(obj):
    if type(obj) == Constant and obj.type == 'int' and obj.value.startswith('0x'):
        return int(obj.value[2:], base=16)
    elif type(obj) == Constant and obj.type == 'int' and obj.value.startswith('0'):
        return int(obj.value[1:], base=8)
    elif type(obj) == Constant and obj.type == 'int':
        return int(obj.value)
    elif type(obj) == BinaryOp and obj.op == '+':
        return static_int(obj.left) + static_int(obj.right)
    elif type(obj) == BinaryOp and obj.op == '-':
        return static_int(obj.left) - static_int(obj.right)
    elif type(obj) == BinaryOp and obj.op == '*':
        return static_int(obj.left) * static_int(obj.right)
    elif type(obj) == BinaryOp and obj.op == '/':
        return static_int(obj.left) / static_int(obj.right)
    elif type(obj) == BinaryOp and obj.op == '%':
        return static_int(obj.left) % static_int(obj.right)
    elif type(obj) == UnaryOp and obj.op == 'sizeof':
        return 1

current_string = -1
# компиляция числа, переменной и т. д.
def compile_obj(obj, root=False):
    global continuel
    global current_string
    global current_function
    global variables
    global functions
    global current_if
    global current_while
    global current_for
    global current_switchl
    global enumerators
    global structs
    global structures
    global structuresnoptrs
    global unions
    global unionlist
    global typedef_structs
    global typedef_unions
    global current_continue
    global current_break
    
    try:
        if obj == None or (type(obj) == Decl and 'extern' in obj.storage) or (type(obj) == Constant and root):
            return ''
        elif type(obj) == Compound:
            code = ''
            for item in obj.block_items:
                code += compile_obj(item) + '\n'
            return code
        elif type(obj) == ExprList:
            code = ''
            for item in obj.exprs:
                code += compile_obj(item, root=True) + '\n'
            return code
        elif type(obj) == ID and obj.name == '__func__':
            current_string += 1
            return '\n"' + current_function + '" ___s' + str(current_string) + '\n&___s' + str(current_string)
        # новая функция
        elif type(obj) == FuncDef:
            code = ''
            # создавать функции получается только в глобальном пространстве имён ('')
            if current_function != '':
                raise Exception('create function: current_function != \'\'')
            #########################################################################
            elif obj.decl.name == 'main':
                code += 'main:\n'
                current_function = 'main'
                
                if obj.decl.type.args != None and len(obj.decl.type.args.params) > 1:
                    if not '___get_args' in functions:
                        print('*** ERROR while compiling main(): please give "-include include/___get_args.h"', file=sys.stderr)
                        return ''
                    
                    code += '/alloc ' + obj.decl.type.args.params[0].name + '\n'
                    code += '/alloc ' + obj.decl.type.args.params[1].name + '\n'
                    code += '{' + obj.decl.type.args.params[1].name + '}' \
                        + ' @___get_args {' + obj.decl.type.args.params[0].name + '} =\n'
            else:
                code += '~' + obj.decl.name + '___END goto\n'
                
                if not obj.decl.name in functions:
                    functions += [obj.decl.name]
                current_function = obj.decl.name
                
                code += obj.decl.name + ': {function}\n'
                
                try:
                    i = 0
                    for param in obj.decl.type.args.params:
                        if type(param) == EllipsisParam:
                            funcfixed[obj.decl.name] = i
                            code += create_var('___vargs', 126)
                            break
                        code += compile_obj(param) + '\n'
                        code += get_var(param.name) + ' =\n'
                        i += 1
                except Exception:
                    ''
                
                if type(obj.decl.type.type) != PtrDecl and type(obj.decl.type.type.type) == IdentifierType and obj.decl.type.type.type.names[0].startswith('__thr'):
                    code += '~' + obj.decl.name + '.___start create_thrd1 0 {return} ' + obj.decl.name + '.___start: thrd_1\n'
                
            
            if obj.body.block_items != None:
                for item in obj.body.block_items:
                    code += compile_obj(item, root=True) + '\n'
            
            if type(obj.decl.type.type) != PtrDecl and type(obj.decl.type.type.type) == IdentifierType and obj.decl.type.type.type.names[0].startswith('__thr'):
                code += '\nhalt thrd_0\n'
            else:
                code += '\n0 ' + ('{return}' if current_function != 'main' else 'exit')
            
            if obj.decl.name != 'main':
                code += '\n' + obj.decl.name + '___END:\n'
            
            current_function = ''
            
            return code
        # новый enum
        elif type(obj) == Decl and type(obj.type) == Enum:
            if obj.type.values != None:
                i = 0
                for item in obj.type.values.enumerators:
                    if item.value != None:
                        i = int(item.value.value)
                    enumerators[item.name] = i
                    i += 1
            return ''
        elif (type(obj) == Typedef) and type(obj.type.type) == Enum:
            if obj.type.type.values != None:
                i = 0
                for item in obj.type.type.values.enumerators:
                    if item.value != None:
                        i = int(item.value.value)
                    enumerators[item.name] = i
                    i += 1
            return ''
        # struct
        elif type(obj) == Decl and type(obj.type) == Struct:
            structs[obj.type.name] = obj.type.decls
            
            return ''
        # union
        elif type(obj) == Decl and type(obj.type) == Union:
            unions[obj.type.name] = obj.type.decls
            
            return ''
        #########################
        elif (type(obj) == Typedef) and type(obj.type) == TypeDecl and type(obj.type.type) == Enum:
            compile_obj(Decl(None, None, None, None, None, obj.type.type, None, None))
            return ''
        # typedef struct ... name
        elif (type(obj) == Typedef) and type(obj.type) == TypeDecl and type(obj.type.type) == Struct:
            if obj.type.type.decls != None:
                structs[obj.name + '___STRUCT'] = obj.type.type.decls
            else:
                structs[obj.name + '___STRUCT'] = structs[obj.type.type.name]
            typedef_structs += [obj.name]
            
            return ''
        elif (type(obj) == Typedef) and type(obj.type) == PtrDecl and type(obj.type.type) == TypeDecl and type(obj.type.type.type) == Struct:
            if obj.type.type.type.decls != None:
                structs[obj.name + '___STRUCT'] = obj.type.type.type.decls
            else:
                structs[obj.name + '___STRUCT'] = structs[obj.type.type.type.name]
            typedef_structs += [obj.name]
            
            return ''
        # typedef union ... name
        elif (type(obj) == Typedef) and type(obj.type) == TypeDecl and type(obj.type.type) == Union:
            if obj.type.type.decls != None:
                unions[obj.name + '___UNION'] = obj.type.type.decls
            else:
                unions[obj.name + '___UNION'] = unions[obj.type.type.name]
            typedef_unions += [obj.name]
            
            return ''
        elif (type(obj) == Typedef) and type(obj.type) == PtrDecl and type(obj.type.type) == TypeDecl and type(obj.type.type.type) == Union:
            if obj.type.type.type.decls != None:
                unions[obj.name + '___UNION'] = obj.type.type.type.decls
            else:
                unions[obj.name + '___UNION'] = unions[obj.type.type.type.name]
            typedef_unions += [obj.name]
            
            return ''
        # структура
        elif type(obj) == Decl and type(obj.type) == TypeDecl and type(obj.type.type) == IdentifierType and obj.type.type.names[0] in typedef_structs:
            name = obj.type.type.names[0] + '___STRUCT'
            
            structures[obj.name] = name
            structuresnoptrs[obj.name] = name
            
            code = ''
            code += '/alloc ' + obj.name + '[' + str(len(structs[name])) + ']\n'
            
            i = 0
            for decl in structs[name]:
                if type(decl.type) == ArrayDecl:
                    code += '/alloc _Array' + str(i) + '___' + name + '[' + str(static_int(decl.type.dim)) + ']\n'
                    code += '{_Array' + str(i) + '___' + name + '} ({' + obj.name + '} ' + str(i) + ' +) =\n'
                i += 1
            
            if obj.init != None and type(obj.init) == InitList:
                for i in range(len(obj.init.exprs)):
                    if type(structs[name][i].type) == ArrayDecl:
                        for j in range(len(obj.init.exprs[i].exprs)):
                            code += compile_obj(obj.init.exprs[i].exprs[j]) + ' ((({' + obj.name + '} ' + str(i) + ' +) .) '+str(j)+' +) =\n'
                    else:
                        code += compile_obj(obj.init.exprs[i]) + ' {' + obj.name + '} ' + ((str(i) + ' + ') if i != 0 else '') + '=\n'
            elif obj.init != None:
                i = 0
                code += compile_obj(obj.init) + '\n'
                for decl in structs[structures[obj.name]]:
                    code += 'dup ' + str(i) + ' + . {' + obj.name + '} ' \
                    + str(i) + ' + =\n'
                    i += 1
                code += 'drop'
            return code
        elif type(obj) == Decl and type(obj.type) == TypeDecl and type(obj.type.type) == Struct:
            name = (obj.type.type.name if obj.type.type.name != None else obj.name + '__STRUCT')
            
            if obj.type.type.name != None and obj.type.type.decls != None:
                structs[obj.type.type.name] = obj.type.type.decls
            
            structures[obj.name] = name
            structuresnoptrs[obj.name] = name
            if obj.type.type.name == None:
                structs[name] = obj.type.type.decls
            
            code = ''
            code += '/alloc ' + obj.name + '[' + str(len(structs[name])) + ']\n'
            
            i = 0
            for decl in structs[name]:
                if type(decl.type) == ArrayDecl:
                    code += '/alloc _Array' + str(i) + '___' + name + '[' + str(static_int(decl.type.dim)) + ']\n'
                    code += '{_Array' + str(i) + '___' + name + '} ({' + obj.name + '} ' + str(i) + ' +) =\n'
                i += 1
            
            if obj.init != None and type(obj.init) == InitList:
                for i in range(len(obj.init.exprs)):
                    if type(structs[name][i].type) == ArrayDecl:
                        for j in range(len(obj.init.exprs[i].exprs)):
                            code += compile_obj(obj.init.exprs[i].exprs[j]) + ' ((({' + obj.name + '} ' + str(i) + ' +) .) '+str(j)+' +) =\n'
                    else:
                        code += compile_obj(obj.init.exprs[i]) + ' {' + obj.name + '} ' + ((str(i) + ' + ') if i != 0 else '') + '=\n'
            elif obj.init != None:
                i = 0
                code += compile_obj(obj.init) + '\n'
                for decl in structs[structures[obj.name]]:
                    code += 'dup ' + str(i) + ' + . {' + obj.name + '} ' \
                    + str(i) + ' + =\n'
                    i += 1
                code += 'drop'
            return code
        # объединение
        elif type(obj) == Decl and type(obj.type) == TypeDecl and type(obj.type.type) == IdentifierType and obj.type.type.names[0] in typedef_unions:
            name = obj.type.type.names[0] + '___UNION'
            unionlist[obj.name] = name
            return '/alloc ' + obj.name + '\n'
        elif type(obj) == Decl and type(obj.type) == TypeDecl and type(obj.type.type) == Union:
            name = (obj.type.type.name if obj.type.type.name != None else obj.name + '__UNION')
            unionlist[obj.name] = name
            if obj.type.type.name == None:
                unions[name] = obj.type.type.decls
        # указатель на объединение
        elif type(obj) == Decl and type(obj.type) == PtrDecl and type(obj.type.type) == TypeDecl and (type(obj.type.type.type) == Union or (type(obj.type.type.type) == IdentifierType and obj.type.type.type.names[0] in typedef_unions)):
            unionlist[obj.name] = (obj.type.type.type.name if type(obj.type.type.type) == Union else (obj.type.type.type.names[0] + '___UNION'))
            
            code = ''
            code += '/alloc ' + obj.name + '\n'
            if obj.init != None:
                code += compile_obj(obj.init) + ' {' + obj.name + '} =\n' 
            
            return code
        # вставить enumerator
        elif type(obj) == ID and (obj.name in enumerators):
            return str(enumerators[obj.name])
        # вставить адрес функции
        elif type(obj) == ID and (obj.name == 'main' or obj.name in functions) and not ('___F___' + obj.name) in variables:
            code = ''
            return code + '\n~' + obj.name
        elif type(obj) == UnaryOp and obj.op == '&' and type(obj.expr) == ID and (obj.expr.name == 'main' or obj.expr.name in functions) and not ('___F___' + obj.expr.name) in variables:
            code = ''
            return code + '\n~' + obj.expr.name
        # присваивание (копирование структуры)
        elif type(obj) == Assignment and obj.op == '=' and type(obj.lvalue) == ID and obj.lvalue.name in structuresnoptrs:
            i = 0
            code = compile_obj(obj.rvalue) + '\n'
            for decl in structs[structures[obj.lvalue.name]]:
                code += 'dup ' + str(i) + ' + . ' + compile_obj(obj.lvalue) + ' ' \
                + str(i) + ' + =\n'
                i += 1
            code += 'drop'
            return code
        # присваивание
        elif type(obj) == Assignment and obj.op == '=':
            return compile_obj(obj.rvalue) + ' ' + compile_obj(obj.lvalue)[:-2] + ' = ' + (compile_obj(obj.lvalue) if not root else '')
        elif type(obj) == Assignment and obj.op[0] in '+-/*^%|&<>' and obj.op.endswith('='):
            return '(' + compile_obj(obj.lvalue) + ' ' + compile_obj(obj.rvalue) + ' ' + obj.op[0].replace('%', 'mod').replace('&', 'and').replace('<', 'lsh').replace('>', 'rsh') + ') ' + compile_obj(obj.lvalue)[:-2] + ' = ' + (compile_obj(obj.lvalue) if not root else '')
        # сложение, вычитание и др.
        elif type(obj) == BinaryOp and obj.op in '-+/*^|%':
            return compile_obj(obj.left) + ' ' + compile_obj(obj.right) + ' ' + obj.op.replace('%', 'mod')
        elif type(obj) == BinaryOp and obj.op == '<<':
            return compile_obj(obj.left) + ' ' + compile_obj(obj.right) + ' lsh'
        elif type(obj) == BinaryOp and obj.op == '>>':
            return compile_obj(obj.left) + ' ' + compile_obj(obj.right) + ' rsh'
        elif type(obj) == BinaryOp and obj.op == '&':
            return compile_obj(obj.left) + ' ' + compile_obj(obj.right) + ' and'
        # if
        elif type(obj) == If:
            code = ''
            saved = current_if
            current_if += 1
            code += compile_cond(obj.cond)
            
            code += ' ~___else' + str(saved) + ' else ' + (';' if current_function == 'main' else '') + '\n'
            
            if type(obj.iftrue) == Compound:
                for item in obj.iftrue.block_items:
                    code += '\t' + compile_obj(item, root=True) + '\n'
            else:
                code += '\t' + compile_obj(obj.iftrue, root=True) + '\n'
            
            code += '~___endif' + str(saved) + ' goto ___else' + str(saved) + ': ' + (';' if current_function == 'main' else '') + '\n'
            
            if obj.iffalse != None and type(obj.iffalse) == Compound:
                for item in obj.iffalse.block_items:
                    code += compile_obj(item, root=True) + '\n'
            elif obj.iffalse != None:
                code += compile_obj(obj.iffalse, root=True) + '\n'
            
            code += '___endif' + str(saved) + ':\n'
            
            return code
        # строка
        elif type(obj) == Constant and obj.type == 'string':
            current_string += 1
            s = preprocess_string(obj.value)
            # для строк, содержащих '\n', '\b' и др.
            for c in s:
                if ord(c) < 32 or ord(c) >= 127:
                    code = '\n'
                    code += '/alloc ___s' + str(current_string) + '[' + str(len(s)+1) + ']\n'
                    i = 0
                    for ch in s:
                        code += str(ord(ch)) + ' ({___s' + str(current_string) + '} ' + str(i) + ' +) =\n'
                        i += 1
                    code += '0 ({___s' + str(current_string) + '} ' + str(i) + ' +) =\n'
                    code += '{___s' + str(current_string) + '}'
                    return code
            return '\n"' + s.replace('"', '`') + '" ___s' + str(current_string) + '\n&___s' + str(current_string)
        # return
        elif type(obj) == Return:
            return (compile_obj(obj.expr) if obj.expr != None else '0') + ' ' + ('{return}' if current_function != 'main' else 'exit')
        # FuncDecl
        elif type(obj) == Decl and type(obj.type) == FuncDecl:
            functions += [obj.name]
            try:
                if type(obj.type.args.params[-1]) == EllipsisParam:
                    funcfixed[obj.name] = len(obj.type.args.params) - 1
            except Exception:
                ''
            return ''
        # создание переменной/массива
        elif type(obj) == DeclList:
            code = ''
            for item in obj.decls:
                code += compile_obj(item) + '\n'
            return code
        elif type(obj) == Decl and type(obj.type) == ArrayDecl and (obj.type.dim != None or obj.init != None):
            code = create_var(obj.name + '__ARRAY__', (static_int(obj.type.dim) if obj.type.dim != None else \
              (len(obj.init.exprs) if type(obj.init) == InitList else len(preprocess_string(obj.init.value)) + 1))) \
                + create_var(obj.name) \
                + get_var(obj.name + '__ARRAY__') + ' ' + get_var(obj.name) + ' =\n'
            
            if obj.init != None and type(obj.init) == InitList:
                for i in range(len(obj.init.exprs)):
                    code += compile_obj(obj.init.exprs[i]) + ' (' + get_var(obj.name + '__ARRAY__') + ' ' + str(i) + ' +) =\n'
            
            elif obj.init != None and type(obj.init) == Constant:
                for i in range(len(preprocess_string(obj.init.value))):
                    code += str(ord(preprocess_string(obj.init.value)[i])) + ' (' + get_var(obj.name + '__ARRAY__') + ' ' + str(i) + ' +) =\n'
                code += '0 (' + get_var(obj.name + '__ARRAY__') + ' ' + str(len(preprocess_string(obj.init.value))) + ' +) =\n'
            
            # если массив является двумерным
            if type(obj.type.type) == ArrayDecl:
                for i in range(static_int(obj.type.dim)):
                    code += create_var(obj.name + '__ARRAY__' + str(i), static_int(obj.type.type.dim)) \
                        + get_var(obj.name + '__ARRAY__' + str(i)) + ' ' \
                        + (get_var(obj.name) + ' . ' + str(i) + ' +') \
                        + ' =\n'
            return code
        elif type(obj) == Decl and (current_function != '' and current_function != 'main') and not 'static' in obj.storage:
            if type(obj.type) == PtrDecl and type(obj.type.type) == TypeDecl and (type(obj.type.type.type) == Struct or (type(obj.type.type.type) == IdentifierType and obj.type.type.type.names[0] in typedef_structs)):
                structures[obj.name] = (obj.type.type.type.name if type(obj.type.type.type) == Struct else (obj.type.type.type.names[0] + '___STRUCT'))
                if obj.name in structuresnoptrs:
                    del structuresnoptrs[obj.name]
            
            code = ''
            if type(obj.type) == TypeDecl and type(obj.type.type) == Enum:
                compile_obj(Decl(None, None, None, None, None, obj.type.type, None, None))
            variables += [current_function + '.' + obj.name]
            code += '/alloc ' + current_function + '.' + obj.name + '___ARRAY__[64]\n'
            code += '/define ' + current_function + '.' + obj.name + ' :{' \
                + current_function + '.' + obj.name + '___ARRAY__} {__retptr}! +' + '\n'
            if obj.init != None:
                code += compile_obj(Assignment('=', ID(current_function + '.' + obj.name), obj.init), root=True) + '\n'
            
            return code
        elif type(obj) == Decl:
            if type(obj.type) == PtrDecl and type(obj.type.type) == TypeDecl and (type(obj.type.type.type) == Struct or (type(obj.type.type.type) == IdentifierType and obj.type.type.type.names[0] in typedef_structs)):
                structures[obj.name] = (obj.type.type.type.name if type(obj.type.type.type) == Struct else (obj.type.type.type.names[0] + '___STRUCT'))
                if obj.name in structuresnoptrs:
                    del structuresnoptrs[obj.name]
            
            code = ''
            if type(obj.type) == TypeDecl and type(obj.type.type) == Enum:
                if obj.type.type.values != None:
                    i = 0
                    for item in obj.type.type.values.enumerators:
                        if item.value != None:
                            i = int(item.value.value)
                        enumerators[item.name] = i
                        i += 1
            code += create_var(obj.name)
            if current_function == '' or obj.init != None:
                code += (compile_obj(obj.init) if obj.init != None else '0') + ' ' + get_var(obj.name) + ' =\n'
            return code
        ######################################################
        elif type(obj) == Cast:
            return compile_obj(obj.expr)
        # тернарный оператор
        elif type(obj) == TernaryOp:
            code = ''
            
            saved = current_if
            current_if += 1
            
            code += compile_cond(obj.cond) + ' ~___tElse' + str(saved) + ' else '
            code += compile_obj(obj.iftrue) + ' ~___tEndif' + str(saved) + ' goto ___tElse' + str(saved) + ': '
            code += compile_obj(obj.iffalse) + ' ___tEndif' + str(saved) + ':'
            
            return code
        # число
        elif type(obj) == Constant and (obj.type == 'int' or obj.type.startswith('unsigned') or obj.type.startswith('long')) and not obj.value.startswith('0'):
            return str(int(obj.value.lower().replace('l', '').replace('u', ''), base=0))
        elif type(obj) == Constant and (obj.type == 'int' or obj.type.startswith('unsigned') or obj.type.startswith('long')) and obj.value.startswith('0x'):
            return str(int(obj.value[2:].lower().replace('l', '').replace('u', ''), base=16))
        elif type(obj) == Constant and (obj.type == 'int' or obj.type.startswith('unsigned') or obj.type.startswith('long')):
            return str(int(obj.value.lower().replace('l', '').replace('u', ''), base=8))
        # символ
        elif type(obj) == Constant and obj.type == 'char':
            return str(ord(preprocess_string(obj.value)))
        # элемент массива
        elif type(obj) == ArrayRef:
            return compile_obj(obj.name) + ' ' + compile_obj(obj.subscript) + ' + .'
        # sizeof
        elif type(obj) == UnaryOp and obj.op == 'sizeof' and type(obj.expr) == ID and \
        ((obj.expr.name + '__ARRAY__') in variables or (current_function + '.' + obj.expr.name + '__ARRAY__') in variables):
            return get_var(obj.expr.name)[:-1] + '__ARRAY__.length}'
        elif type(obj) == UnaryOp and obj.op == 'sizeof' and type(obj.expr) == Typename and \
        type(obj.expr.type) == TypeDecl and type(obj.expr.type.type) == Struct and \
        obj.expr.type.type.name in structs:
            return str(len(structs[obj.expr.type.type.name]))
        elif type(obj) == UnaryOp and obj.op == 'sizeof' and type(obj.expr) == Typename and \
        type(obj.expr.type) == TypeDecl and type(obj.expr.type.type) == IdentifierType and \
        obj.expr.type.type.names[0] in typedef_structs:
            return str(len(structs[obj.expr.type.type.names[0] + '___STRUCT']))
        elif type(obj) == UnaryOp and obj.op == 'sizeof' and type(obj.expr) == StructRef:
            for decl in structs[structures[obj.expr.name.name]]:
                if decl.name == obj.expr.field.name:
                    if type(decl.type) == ArrayDecl:
                        return str(static_int(decl.type.dim))
                    else:
                        return '1'
            return '0'
        elif type(obj) == UnaryOp and obj.op == 'sizeof':
            return '1'
        # -выражение
        elif type(obj) == UnaryOp and obj.op == '-':
            return compile_obj(obj.expr) + ' neg'
        # +выражение
        elif type(obj) == UnaryOp and obj.op == '+':
            return compile_obj(obj.expr)
        # ~выражение
        elif type(obj) == UnaryOp and obj.op == '~':
            return compile_obj(obj.expr) + ' neg --'
        # поле объединения/структуры
        elif type(obj) == StructRef and obj.type == '.' and type(obj.name) == ID and obj.name.name in unionlist:
            return '{' + obj.name.name + '} .'
        elif type(obj) == StructRef and obj.type == '->' and type(obj.name) == ID and obj.name.name in unionlist:
            return '{' + obj.name.name + '}'
        elif type(obj) == StructRef:
            i = 0
            struct = []
            if type(obj.name) == Cast and type(obj.name.to_type.type) == TypeDecl and type(obj.name.to_type.type.type) == Struct:
                struct = structs[obj.name.to_type.type.type.name].copy()
            elif type(obj.name) == Cast and type(obj.name.to_type.type) == PtrDecl and type(obj.name.to_type.type.type) == TypeDecl and type(obj.name.to_type.type.type.type) == Struct:
                struct = structs[obj.name.to_type.type.type.type.name].copy()
            elif type(obj.name) == Cast and type(obj.name.to_type.type) == TypeDecl and type(obj.name.to_type.type.type) == IdentifierType:
                struct = structs[obj.name.to_type.type.type.names[0] + '___STRUCT'].copy()
            elif type(obj.name) == Cast and type(obj.name.to_type.type) == PtrDecl and type(obj.name.to_type.type.type) == TypeDecl and type(obj.name.to_type.type.type.type) == IdentifierType:
                struct = structs[obj.name.to_type.type.type.type.names[0] + '___STRUCT'].copy()
            else:
                struct = structs[structures[obj.name.name]].copy()
            while struct[i].name != obj.field.name:
                i += 1
            return compile_obj(obj.name)[:(-2 if obj.type == '.' else None)] + ' ' + ((str(i) + ' + ') if i != 0 else '') + '.'
        # вызов функции (1)
        elif type(obj) == FuncCall and (type(obj.name) != ID or (obj.name.name in variables or (current_function + '.' + obj.name.name) in variables)):
            code = ''
            
            exprs = []
            if obj.args != None:
                exprs += obj.args.exprs
            exprs.reverse()
            
            for o in exprs:
                code += compile_obj(o) + '\n'
            
            code += '~____C' + str(continuel) + ' ' + compile_obj(obj.name) + ' goto ____C' + str(continuel) + ':\n'
            continuel += 1
            
            return code
        ###################
        elif type(obj) == ID and obj.name in structuresnoptrs:
            return get_var(obj.name) + '  '
        # переменная
        elif type(obj) == ID:
            return get_var(obj.name) + ' .'
        # создание метки и переход
        elif type(obj) == Label:
            return '___L' + current_function + '___' + obj.name + ':\n' + compile_obj(obj.stmt)
        elif type(obj) == Goto:
            return '~___L' + current_function + '___' + obj.name + ' goto'
        elif type(obj) == FuncCall and obj.name.name == '__jump' and not obj.name.name in functions:
            return compile_obj(obj.args.exprs[0]) + ' goto'
        ###################################
        elif type(obj) == FuncCall and obj.name.name == '__extern_label' and not obj.name.name in functions:
            return '<' + obj.args.exprs[0].value[1:-1] + '>'
        elif type(obj) == FuncCall and obj.name.name == '_call' and not obj.name.name in functions:
            code = ''
            exprs = []
            if obj.args != None:
                exprs += obj.args.exprs[1:]
            if obj.name.name in functions:
                exprs.reverse()
            for o in exprs:
                code += compile_obj(o) + ' '
            code += preprocess_string(obj.args.exprs[0].value)
            return code
        # printf
        elif type(obj) == FuncCall and obj.name.name == 'printf' and not obj.name.name in functions:
            s_format = preprocess_string(obj.args.exprs[0].value)
            etc = []
            etc += obj.args.exprs[1:]
            ptr = 0
            
            code = ''
            
            i = 0
            while i < len(s_format):
                if s_format[i] == '%' and s_format[i + 1] == '%':
                    code += '\'%\' putc '
                    i += 1
                elif s_format[i] == '%' and s_format[i + 1] == 'c':
                    code += compile_obj(etc[ptr]) + ' putc '
                    ptr += 1
                    i += 1
                elif s_format[i] == '%' and s_format[i + 1] == 's':
                    code += compile_obj(etc[ptr]) + ' puts '
                    ptr += 1
                    i += 1
                elif s_format[i] == '%' and (s_format[i + 1] == 'd' or s_format[i + 1] == 'u' or s_format[i + 1] == 'i' or s_format[i + 1] == 'p'):
                    code += compile_obj(etc[ptr]) + ' putn '
                    ptr += 1
                    i += 1
                elif s_format[i] == '\n':
                    code += 'newline '
                elif s_format[i] == '\b':
                    code += 'backspace '
                elif s_format[i] == '\r':
                    code += 'cr '
                else:
                    code += str(ord(s_format[i])) + ' putc '
                
                i += 1
            return code
        # вызов функции (2)
        elif type(obj) == FuncCall:
            code = ''
            
            exprs = []
            vargs = []
            if obj.args != None:
                exprs += obj.args.exprs
            if obj.name.name in functions:
                if obj.name.name in funcfixed:
                    vargs += exprs[funcfixed[obj.name.name]:]
                    exprs = exprs[:funcfixed[obj.name.name]]
                exprs.reverse()
            for o in exprs:
                code += compile_obj(o) + '\n'
            i = 0
            for o in vargs:
                code += compile_obj(o) + ' ({' + obj.name.name + '.___vargs} ' + str(i) + ' +) =\n'
                i += 1
            code += ('@' if obj.name.name in functions else '') + obj.name.name
            if (obj.name.name in functions or obj.name.name == 'memset' or obj.name.name == 'memcpy' or obj.name.name == 'getc') and root:
                code += ' drop'
            return code
        # инкремент и декремент
        elif type(obj) == UnaryOp and obj.op == '++':
            return '(' + compile_obj(obj.expr) + ' ++) ' + compile_obj(obj.expr)[:-2] + ' = ' + (compile_obj(obj.expr) if not root else '')
        elif type(obj) == UnaryOp and obj.op == '--':
            return '(' + compile_obj(obj.expr) + ' --) ' + compile_obj(obj.expr)[:-2] + ' = ' + (compile_obj(obj.expr) if not root else '')
        elif type(obj) == UnaryOp and obj.op == 'p++':
            return (compile_obj(obj.expr) if not root else '') + ' (' + compile_obj(obj.expr) + ' ++) ' + compile_obj(obj.expr)[:-2] + ' ='
        elif type(obj) == UnaryOp and obj.op == 'p--':
            return (compile_obj(obj.expr) if not root else '') + ' (' + compile_obj(obj.expr) + ' --) ' + compile_obj(obj.expr)[:-2] + ' ='
        # получение адреса переменной/массива/элемента массива/структуры
        elif type(obj) == UnaryOp and obj.op == '&' and type(obj.expr) == ID and obj.expr.name in structures:
            return '{' + obj.expr.name + '}'
        elif type(obj) == UnaryOp and obj.op == '&':
            return compile_obj(obj.expr)[:-2]
        # *expr
        elif type(obj) == UnaryOp and obj.op == '*':
            return compile_obj(obj.expr) + ' .'
        # while
        elif type(obj) == While:
            code = ''
            saved = current_while
            current_while += 1
            current_continue = '___while' + str(saved)
            current_break = '___endwhile' + str(saved)
            code += '___while' + str(saved) + ': ' + compile_cond(obj.cond)
            
            code += ' ~___endwhile' + str(saved) + ' else ' + (';' if current_function == 'main' else '') + '\n'
            
            if type(obj.stmt) == Compound:
                for item in obj.stmt.block_items:
                    current_continue = '___while' + str(saved)
                    current_break = '___endwhile' + str(saved)
                    code += '\t' + compile_obj(item, root=True) + '\n'
            else:
                code += '\t' + compile_obj(obj.stmt, root=True) + '\n'
            
            code += '~___while' + str(saved) + ' goto ___endwhile' + str(saved) + ':'
            
            return code
        # do-while
        elif type(obj) == DoWhile:
            code = ''
            saved = current_while
            current_while += 1
            current_continue = '___dowhile' + str(saved)
            current_break = '___enddowhile' + str(saved)
            code += '___dowhile' + str(saved) + ':\n'
            
            if type(obj.stmt) == Compound:
                for item in obj.stmt.block_items:
                    current_continue = '___dowhile' + str(saved)
                    current_break = '___enddowhile' + str(saved)
                    code += '\t' + compile_obj(item, root=True) + '\n'
            else:
                code += '\t' + compile_obj(obj.stmt, root=True) + '\n'
            
            code += compile_cond(obj.cond) + ' ~___dowhile' + str(saved) + ' then ___enddowhile' + str(saved) + ':\n'
            
            return code
        # for
        elif type(obj) == For:
            code = ''
            saved = current_for
            current_for += 1
            current_continue = '___preendfor' + str(saved)
            current_break = '___endfor' + str(saved)
            code += compile_obj(obj.init, root=True) + ' '
            code += '___for' + str(saved) + ': ' + compile_cond(obj.cond)
            
            code += ' ~___endfor' + str(saved) + ' else ' + (';' if current_function == 'main' else '') + '\n'
            
            if type(obj.stmt) == Compound:
                for item in obj.stmt.block_items:
                    current_continue = '___preendfor' + str(saved)
                    current_break = '___endfor' + str(saved)
                    code += '\t' + compile_obj(item, root=True) + '\n'
            else:
                code += '\t' + compile_obj(obj.stmt, root=True) + '\n'
            
            code += '___preendfor' + str(saved) + ': ' + compile_obj(obj.next, root=True) + ' ~___for' + str(saved) + ' goto ___endfor' + str(saved) + ':'
            
            return code
        # switch
        elif type(obj) == Switch:
            code = ''
            
            saved = current_switchl
            current_switchl += 1
            
            i = 0
            
            code += compile_obj(obj.cond) + '\n'
            
            for item in obj.stmt.block_items:
                if type(item) != Default:
                    code += 'dup ' + compile_obj(item.expr) + ' =? ~___switchl' + str(saved) + '_' + str(i) + ' then\n'
                i += 1
            code += 'drop\n'
            i = 0
            
            for item in obj.stmt.block_items:
                if type(item) == Default:
                    code += '~___switchl' + str(saved) + '_' + str(i) + ' goto\n'
                
                i += 1
            
            code += '~___endswitchl' + str(saved) + ' goto\n'
            
            i = 0
            
            for item in obj.stmt.block_items:
                code += '___switchl' + str(saved) + '_' + str(i) + ':\n'
                for o in item.stmts:
                    current_break = '___endswitchl' + str(saved)
                    code += '\t' + compile_obj(o, root=True) + '\n'
                
                i += 1
            
            code += '___endswitchl' + str(saved) + ':\n'
            
            return code
        ####################
        elif type(obj) == Continue:
            return '~' + current_continue + ' goto'
        elif type(obj) == Break:
            return '~' + current_break + ' goto'
        elif type(obj) == BinaryOp or type(obj) == UnaryOp:
            return compile_cond(obj)
        elif type(obj) == EmptyStatement or type(obj) == Typedef:
            return ''
        else:
            return '# (unknown) #\n'
    except Exception as e:
        print('*** compile_obj() error (\n\t' + str(e) + '\n)', file=sys.stderr)
        return ''

################################################################################

if __name__ == '__main__':
    import sys
    from pycparser import parse_file
    
    if len(sys.argv) == 1:
        print('usage: ./c2xcc.py FILE ["CPP_ARGS"] [> OUT_FILE]')
        sys.exit(1)
    
    cppargs = ['-undef', '-D__XCC_C__=1']
    if len(sys.argv) > 2:
        cppargs += sys.argv[2].split(' ')
    ast = parse_file(sys.argv[1], use_cpp=True, cpp_args=cppargs)
    
    print(get_init_code())
    for item in ast:
        print(compile_obj(item, root=True))

