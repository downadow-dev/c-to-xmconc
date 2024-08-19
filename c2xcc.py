#!/usr/bin/python3

from pycparser.c_ast import *


current_function = ''   # мы находимся в теле этой функции
                        # (пока лишь в глобальном пространстве имён)

variables = []          # переменные
functions = []          # функции

current_if = 0
current_for = 0
current_while = 0
current_switchl = 0
current_continue = ''
current_break = ''

enumerators = {}
structs = {}
structures = {}

typedef_structs = []

def reset():
    global variables
    variables = []
    global functions
    functions = []
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
    global structs
    structs = {}
    global typedef_structs
    typedef_structs = []
    global current_continue
    current_continue = ''
    global current_break
    current_break = ''

# получить переменную/массив
def get_var(name):
    if current_function == '' or not (current_function + '.' + name) in variables:
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
            return compile_obj(op)
    
    else:
        return compile_obj(op)


def static_int(obj):
    if type(obj) == Constant and obj.type == 'int':
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

current_string = -1
# компиляция числа, переменной и т. д.
def compile_obj(obj, root=False):
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
    global typedef_structs
    global current_continue
    global current_break
    
    try:
        if obj == None:
            return ''
        elif type(obj) == ExprList:
            code = ''
            for item in obj.exprs:
                code += compile_obj(item) + '\n'
            return code
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
            else:
                code += '~' + obj.decl.name + '___END goto\n'
                
                if not obj.decl.name in functions:
                    functions += [obj.decl.name]
                current_function = obj.decl.name
                
                code += obj.decl.name + ': {function}\n'
                
                try:
                    for param in obj.decl.type.args.params:
                        code += compile_obj(param) + '\n'
                        code += get_var(param.name) + ' =\n'
                except Exception:
                    print('', file=sys.stderr)
                
                if type(obj.decl.type.type) != PtrDecl and obj.decl.type.type.type.names[0].startswith('__thr'):
                    code += '~' + obj.decl.name + '.___start create_thrd1 {return} ' + obj.decl.name + '.___start: thrd_1\n'
                
            
            if obj.body.block_items != None:
                for item in obj.body.block_items:
                    code += compile_obj(item, root=True) + '\n'
            
            if type(obj.decl.type.type) != PtrDecl and obj.decl.type.type.type.names[0].startswith('__thr'):
                code += '\nhalt thrd_0\n'
            else:
                code += '\n' + ('{return}' if current_function != 'main' else '0 exit')
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
        # struct
        elif type(obj) == Decl and type(obj.type) == Struct:
            structs[obj.type.name] = obj.type.decls;
            
            return ''
        # typedef struct { ... } name
        elif (type(obj) == Typedef) and type(obj.type) == TypeDecl and type(obj.type.type) == Struct:
            if obj.type.type.decls != None:
                structs[obj.name + '___STRUCT'] = obj.type.type.decls
            else:
                structs[obj.name + '___STRUCT'] = structs[obj.type.type.name]
            typedef_structs += [obj.name]
            
            return ''
        # структура
        elif type(obj) == Decl and type(obj.type) == TypeDecl and type(obj.type.type) == IdentifierType and obj.type.type.names[0] in typedef_structs:
            name = obj.type.type.names[0] + '___STRUCT'
            
            structures[obj.name] = name
            
            code = ''
            code += '/alloc ' + obj.name + '[' + str(len(structs[name])) + ']\n'
            
            if obj.init != None and type(obj.init) == InitList:
                for i in range(len(obj.init.exprs)):
                    code += compile_obj(obj.init.exprs[i]) + ' ({' + obj.name + '} ' + str(i) + ' +) =\n'
            
            return code
        elif type(obj) == Decl and type(obj.type) == TypeDecl and type(obj.type.type) == Struct:
            name = (obj.type.type.name if obj.type.type.name != None else obj.name + '__STRUCT')
            
            structures[obj.name] = name
            if obj.type.type.name == None:
                structs[name] = obj.type.type.decls
            
            code = ''
            code += '/alloc ' + obj.name + '[' + str(len(structs[name])) + ']\n'
            
            if obj.init != None and type(obj.init) == InitList:
                for i in range(len(obj.init.exprs)):
                    code += compile_obj(obj.init.exprs[i]) + ' ({' + obj.name + '} ' + str(i) + ' +) =\n'
            
            return code
        # указатель на структуру
        elif type(obj) == Decl and type(obj.type) == PtrDecl and type(obj.type.type) == TypeDecl and type(obj.type.type.type) == Struct:
            structures[obj.name] = obj.type.type.type.name
            
            code = ''
            code += '/alloc ' + obj.name + '\n'
            if obj.init != None:
                code += compile_obj(obj.init) + ' {' + obj.name + '} =\n' 
            
            return code
        # вставить enumerator
        elif type(obj) == ID and (obj.name in enumerators):
            return str(enumerators[obj.name])
        # вставить адрес функции
        elif type(obj) == ID and (obj.name == 'main' or obj.name in functions):
            return '~' + obj.name
        # присваивание
        elif type(obj) == Assignment and obj.op == '=':
            return compile_obj(obj.rvalue) + ' ' + compile_obj(obj.lvalue)[:-2] + ' = ' + (compile_obj(obj.lvalue) if not root else '')
        elif type(obj) == Assignment and obj.op[0] in '+-/*^%|&' and obj.op.endswith('='):
            return '(' + compile_obj(obj.lvalue) + ' ' + compile_obj(obj.rvalue) + ' ' + obj.op[0].replace('%', 'mod').replace('&', 'and') + ') ' + compile_obj(obj.lvalue)[:-2] + ' = ' + (compile_obj(obj.lvalue) if not root else '')
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
            return '\n"' + preprocess_string(obj.value) + '" ___s' + str(current_string) + '\n&___s' + str(current_string)
        # return
        elif type(obj) == Return:
            return compile_obj(obj.expr) + ' ' + ('{return}' if current_function != 'main' else 'exit')
        # FuncDecl
        elif type(obj) == Decl and type(obj.type) == FuncDecl and current_function == '':
            functions += [obj.name]
            return ''
        # создание переменной/массива
        elif type(obj) == DeclList:
            code = ''
            for item in obj.decls:
                code += compile_obj(item) + '\n'
            return code
        elif type(obj) == Decl and type(obj.type) == ArrayDecl and (obj.type.dim != None or obj.init != None):
            code = create_var(obj.name + '__ARRAY__', (static_int(obj.type.dim) if obj.type.dim != None else len(obj.init.exprs))) \
                + create_var(obj.name) \
                + get_var(obj.name + '__ARRAY__') + ' ' + get_var(obj.name) + ' =\n'
            if obj.init != None and type(obj.init) == InitList:
                for i in range(len(obj.init.exprs)):
                    code += compile_obj(obj.init.exprs[i]) + ' ({' + obj.name + '__ARRAY__' + '} ' + str(i) + ' +) =\n'
            # если массив является двумерным
            if type(obj.type.type) == ArrayDecl:
                for i in range(static_int(obj.type.dim)):
                    code += create_var(obj.name + '__ARRAY__' + str(i), static_int(obj.type.type.dim)) \
                        + get_var(obj.name + '__ARRAY__' + str(i)) + ' ' \
                        + (get_var(obj.name) + ' . ' + str(i) + ' +') \
                        + ' =\n'
            return code
        elif type(obj) == Decl and (current_function != '' and current_function != 'main') and not 'static' in obj.storage:
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
            code = ''
            if type(obj.type) == TypeDecl and type(obj.type.type) == Enum:
                compile_obj(Decl(None, None, None, None, None, obj.type.type, None, None))
            code += create_var(obj.name)
            if obj.init != None:
                code += compile_obj(Assignment('=', ID(obj.name), obj.init), root=True) + '\n'
            return code
        ######################################################
        elif type(obj) == Cast:
            return compile_obj(obj.expr)
        # (a == b ? c : d) и др.
        elif type(obj) == TernaryOp:
            code = ''
            
            code += compile_cond(obj.cond) + ' ~___tElse' + str(current_if) + ' else '
            code += compile_obj(obj.iftrue) + ' ~___tEndif' + str(current_if) + ' goto ___tElse' + str(current_if) + ': '
            code += compile_obj(obj.iffalse) + ' ___tEndif' + str(current_if) + ':'
            
            current_if += 1
            
            return code
        # число
        elif type(obj) == Constant and obj.type == 'int' and not obj.value.startswith('0'):
            return str(int(obj.value, base=0))
        elif type(obj) == Constant and obj.type == 'int' and obj.value.startswith('0x'):
            return str(int(obj.value[2:], base=16))
        elif type(obj) == Constant and obj.type == 'int':
            return str(int(obj.value, base=8))
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
        elif type(obj) == UnaryOp and obj.op == 'sizeof':
            return '1'
        # -выражение
        elif type(obj) == UnaryOp and obj.op == '-':
            return compile_obj(obj.expr) + ' neg'
        # ~выражение
        elif type(obj) == UnaryOp and obj.op == '~':
            return compile_obj(obj.expr) + ' neg --'
        # поле структуры
        elif type(obj) == StructRef and obj.type == '.':
            i = 0
            while structs[structures[obj.name.name]][i].name != obj.field.name:
                i += 1
            return '{' + obj.name.name + '} ' + str(i) + ' + .'
        elif type(obj) == StructRef and obj.type == '->':
            i = 0
            while structs[structures[obj.name.name]][i].name != obj.field.name:
                i += 1
            return '{' + obj.name.name + '}! ' + str(i) + ' + .'
        # переменная
        elif type(obj) == ID:
            return get_var(obj.name) + ' .'
        # создание метки и переход
        elif type(obj) == Label:
            return '___L' + current_function + '___' + obj.name + ':\n' + compile_obj(obj.stmt)
        elif type(obj) == Goto:
            return '~___L' + current_function + '___' + obj.name + ' goto'
        # printf
        elif type(obj) == FuncCall and obj.name.name == 'printf':
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
                elif s_format[i] == '%' and (s_format[i + 1] == 'd' or s_format[i + 1] == 'u'):
                    code += compile_obj(etc[ptr]) + ' putn '
                    ptr += 1
                    i += 1
                elif s_format[i] == '\n':
                    code += 'newline '
                elif s_format[i] == '\b':
                    code += 'backspace '
                else:
                    code += str(ord(s_format[i])) + ' putc '
                
                i += 1
            return code
        # вызов функции
        elif type(obj) == FuncCall:
            code = ''
            exprs = []
            if obj.args != None:
                exprs += obj.args.exprs
            if obj.name.name in functions:
                exprs.reverse()
            for o in exprs:
                code += compile_obj(o) + ' '
            code += ('@' if obj.name.name in functions else '') + obj.name.name
            return code
        # инкремент и декремент
        elif type(obj) == UnaryOp and obj.op == '++' and type(obj.expr) == ID:
            return '(' + get_var(obj.expr.name) + ' . ++) ' + get_var(obj.expr.name) + ' = ' + (get_var(obj.expr.name) + ' .' if not root else '')
        elif type(obj) == UnaryOp and obj.op == '--' and type(obj.expr) == ID:
            return '(' + get_var(obj.expr.name) + ' . --) ' + get_var(obj.expr.name) + ' = ' + (get_var(obj.expr.name) + ' .' if not root else '')
        elif type(obj) == UnaryOp and obj.op == 'p++' and type(obj.expr) == ID:
            return (get_var(obj.expr.name) + ' .' if not root else '') + ' (' + get_var(obj.expr.name) + ' . ++) ' + get_var(obj.expr.name) + ' ='
        elif type(obj) == UnaryOp and obj.op == 'p--' and type(obj.expr) == ID:
            return (get_var(obj.expr.name) + ' .' if not root else '') + ' (' + get_var(obj.expr.name) + ' . --) ' + get_var(obj.expr.name) + ' ='
        
        elif type(obj) == UnaryOp and obj.op == '++' and (type(obj.expr) == ArrayRef or type(obj.expr) == StructRef):
            return '(' + compile_obj(obj.expr) + ' ++) ' + compile_obj(obj.expr)[:-2] + ' = ' + (compile_obj(obj.expr) if not root else '')
        elif type(obj) == UnaryOp and obj.op == '--' and (type(obj.expr) == ArrayRef or type(obj.expr) == StructRef):
            return '(' + compile_obj(obj.expr) + ' --) ' + compile_obj(obj.expr)[:-2] + ' = ' + (compile_obj(obj.expr) if not root else '')
        elif type(obj) == UnaryOp and obj.op == 'p++' and (type(obj.expr) == ArrayRef or type(obj.expr) == StructRef):
            return (compile_obj(obj.expr) if not root else '') + ' (' + compile_obj(obj.expr) + ' ++) ' + compile_obj(obj.expr)[:-2] + ' ='
        elif type(obj) == UnaryOp and obj.op == 'p--' and (type(obj.expr) == ArrayRef or type(obj.expr) == StructRef):
            return (compile_obj(obj.expr) if not root else '') + ' (' + compile_obj(obj.expr) + ' --) ' + compile_obj(obj.expr)[:-2] + ' ='
        # получение адреса переменной/массива/элемента массива/структуры/поля
        elif type(obj) == UnaryOp and obj.op == '&' and type(obj.expr) == ID and obj.expr.name in structures:
            return '{' + obj.expr.name + '}'
        elif type(obj) == UnaryOp and obj.op == '&' and type(obj.expr) == StructRef and obj.expr.type == '.':
            i = 0
            while structs[structures[obj.expr.name.name]][i].name != obj.expr.field.name:
                i += 1
            return '{' + obj.expr.name.name + '} ' + str(i) + ' +'
        elif type(obj) == UnaryOp and obj.op == '&' and type(obj.expr) == StructRef and obj.expr.type == '->':
            i = 0
            while structs[structures[obj.expr.name.name]][i].name != obj.expr.field.name:
                i += 1
            return '{' + obj.expr.name.name + '}! ' + str(i) + ' +'
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
            current_continue = '___for' + str(saved)
            current_break = '___endfor' + str(saved)
            code += compile_obj(obj.init, root=True) + ' '
            code += '___for' + str(saved) + ': ' + compile_cond(obj.cond)
            
            code += ' ~___endfor' + str(saved) + ' else ' + (';' if current_function == 'main' else '') + '\n'
            
            if type(obj.stmt) == Compound:
                for item in obj.stmt.block_items:
                    code += '\t' + compile_obj(item, root=True) + '\n'
            else:
                code += '\t' + compile_obj(obj.stmt, root=True) + '\n'
            
            code += compile_obj(obj.next, root=True) + ' ~___for' + str(saved) + ' goto ___endfor' + str(saved) + ':'
            
            return code
        # switch
        elif type(obj) == Switch:
            code = ''
            
            saved = current_switchl
            current_switchl += 1
            
            for item in obj.stmt.block_items:
                if type(item) != Default:
                    code += compile_obj(obj.cond) + ' ' + compile_obj(item.expr) + ' =?'
                    code += ' ~___switchl' + str(current_switchl) + ' else ' + (';' if current_function == 'main' else '') + '\n'
                
                for o in item.stmts:
                    code += '\t' + compile_obj(o, root=True) + '\n'
                
                code += '~___endcase' + str(saved) + ' goto ___switchl' + str(current_switchl) + ': ' + (';' if current_function == 'main' else '') + '\n'
                
                current_switchl += 1
            code += '___switchl' + str(current_switchl - 1) + ':\n'
            code += '___endcase' + str(saved) + ':\n'
            
            return code
        ####################
        elif type(obj) == Continue:
            return '~' + current_continue + ' goto'
        elif type(obj) == Break:
            return '~' + current_break + ' goto'
        elif type(obj) == BinaryOp:
            return compile_cond(obj)
        elif type(obj) == EmptyStatement or type(obj) == Typedef:
            return ''
        else:
            return '# (unknown) #\n'
    except Exception:
        print('*** compile_obj() error', file=sys.stderr)
        return ''

################################################################################

if __name__ == '__main__':
    import sys
    from pycparser import parse_file
    
    if len(sys.argv) == 1:
        print('usage: ./c2xcc.py FILE [CPP_ARG] [> OUT_FILE]')
        sys.exit(1)
    
    cppargs = ['-D__XCC_C__=1']
    if len(sys.argv) > 2:
        cppargs += [sys.argv[2]]
    ast = parse_file(sys.argv[1], use_cpp=True, cpp_args=cppargs)
    
    print(get_init_code())
    for item in ast:
        print(compile_obj(item, root=True))

