#!/usr/bin/python3

from pycparser.c_ast import *


current_function = ''   # мы находимся в теле этой функции
                        # (пока лишь в глобальном пространстве имён)

variables = []          # переменные
functions = []          # функции
arrays = []

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
typedefs = {}

# получить переменную/массив
def get_var(name):
    if ('___F___' + name) in variables:
        return '{___F___' + name + '}'
    elif current_function == '' or not (current_function + '.' + name) in variables:
        return '{' + name + '}'
    else:
        return '{' + current_function + '.' + name + '}'

def is_array(name):
    return ((current_function != '' and (current_function + '.' + name) in arrays) or name in arrays)

# создаёт переменную/массив
def create_var(name, array_len=0):
    global variables
    global arrays
    
    if current_function != '':
        name = current_function + '.' + name
    
    if not name in variables:
        variables += [name]
    if not name in arrays and array_len > 0:
        arrays += [name]
    elif name in arrays and array_len <= 0:
        for i in range(len(arrays)):
            if arrays[i] == name:
                del arrays[i]
                break
    return '/alloc ' + name + ('[' + str(array_len) + ']' if array_len > 0 else '') + '\n'

def get_struct_length(struct):
    l = 0
    for decl in struct:
        if type(decl.type) == ArrayDecl:
            l += static_int(decl.type.dim)
        elif type(decl.type) == TypeDecl and type(decl.type.type) == Struct:
            l += get_struct_length(structs[decl.type.type.name])
        else:
            l += 1
    return l

def get_struct(obj):
    struct = []
    
    obj = preprocess_typedefs(obj)
    
    if type(obj) == ID:
        return structs[structures[obj.name]].copy()
    elif type(obj) == ArrayRef:
        return get_struct(obj.name)
    elif type(obj) == UnaryOp:
        return get_struct(obj.expr)
    elif type(obj) == BinaryOp:
        return get_struct(obj.left)
    # (struct NAME)
    elif type(obj) == Cast and type(obj.to_type.type) == TypeDecl and type(obj.to_type.type.type) == Struct:
        struct = structs[obj.to_type.type.type.name].copy()
    # (struct NAME *)
    elif type(obj) == Cast and type(obj.to_type.type) == PtrDecl and type(obj.to_type.type.type) == TypeDecl and type(obj.to_type.type.type.type) == Struct:
        struct = structs[obj.to_type.type.type.type.name].copy()
    # id
    elif type(obj) == ID:
        struct = structs[structures[obj.name]].copy()
    # StructRef
    elif type(obj) == StructRef:
        struct = get_struct(obj.name)
        for decl in struct:
            if obj.field.name == decl.name:
                decl.type = preprocess_typedefs(decl.type)
                if type(decl.type) == TypeDecl and type(decl.type.type) == Struct:
                    return structs[decl.type.type.name].copy()
                elif type(decl.type) == PtrDecl and type(decl.type.type) == TypeDecl and type(decl.type.type.type) == Struct:
                    return structs[decl.type.type.type.name].copy()
                else:
                    raise Exception('StructRef error')
                    return []
    # ?
    else:
        raise Exception('StructRef error')
        return []
    return struct

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
/define ___function :({___ret} {__retptr}! +) = ({__retptr}! ++) {__retptr} =
/define return :({__retptr}! --) {__retptr} = (({___ret} {__retptr}! +) .) goto
'''

# "2 == 4" => "2 4 =?" и т. д.
def compile_cond(op):
    global current_if
    
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
            code = ''
            saved = current_if
            current_if += 1
            code += compile_cond(op.left) + ' dup ~___ANDend' + str(saved) + ' else drop '
            code += compile_cond(op.right) + ' ___ANDend' + str(saved) + ':'
            return code
        elif op.op == '||':
            code = ''
            saved = current_if
            current_if += 1
            code += compile_cond(op.left) + ' dup ~___ORend' + str(saved) + ' then drop '
            code += compile_cond(op.right) + ' ___ORend' + str(saved) + ':'
            return code
        
        else:
            return compile_obj(op) + ' 0 !?'
    
    else:
        return compile_obj(op) + ' 0 !?'


def static_int(obj):
    if type(obj) == Constant and obj.type == 'int' and obj.value == '0':
        return 0
    elif type(obj) == Constant and obj.type == 'int' and obj.value.startswith('0x'):
        return int(obj.value[2:], base=16)
    elif type(obj) == Constant and obj.type == 'int' and obj.value.startswith('0'):
        return int(obj.value[1:], base=8)
    elif type(obj) == Constant and obj.type == 'int':
        return int(obj.value, base=10)
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
    elif type(obj) == BinaryOp and obj.op == '^':
        return static_int(obj.left) ^ static_int(obj.right)
    elif type(obj) == BinaryOp and obj.op == '<<':
        return static_int(obj.left) << static_int(obj.right)
    elif type(obj) == BinaryOp and obj.op == '>>':
        return static_int(obj.left) >> static_int(obj.right)
    elif type(obj) == BinaryOp and obj.op == '|':
        return static_int(obj.left) | static_int(obj.right)
    elif type(obj) == BinaryOp and obj.op == '&':
        return static_int(obj.left) & static_int(obj.right)
    elif type(obj) == UnaryOp and obj.op == 'sizeof':
        return 1

def preprocess_typedefs(obj):
    if type(obj) == Decl:
        obj.type = preprocess_typedefs(obj.type)
    elif type(obj) == TypeDecl and type(obj.type) == IdentifierType and obj.type.names[0] in typedefs:
        obj = typedefs[obj.type.names[0]]
    elif (type(obj) == PtrDecl or type(obj) == ArrayDecl):
        obj.type = preprocess_typedefs(obj.type)
    elif type(obj) == Cast:
        obj.to_type.type = preprocess_typedefs(obj.to_type.type)
    
    if type(obj) == PtrDecl and type(obj.type) == PtrDecl:
        obj.type = preprocess_typedefs(obj.type.type)
    
    return obj

current_string = -1
# компиляция числа, переменной и т. д.
def compile_obj(obj, root=False):
    global continuel
    global current_string
    global current_function
    global variables
    global arrays
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
    global current_continue
    global current_break
    global typedefs
    
    try:
        obj = preprocess_typedefs(obj)
        
        if (type(obj) == Typedef) and not obj.name.startswith('__thr'):
            typedefs[obj.name] = preprocess_typedefs(obj.type)
            return ''
        elif obj == None or (type(obj) == Decl and 'extern' in obj.storage) or ((type(obj) == Constant or type(obj) == Cast) and root):
            return ''
        elif type(obj) == Compound:
            code = ''
            for item in obj.block_items:
                code += compile_obj(item) + '\n'
            return code
        elif type(obj) == NamedInitializer:
            return compile_obj(obj.expr)
        elif type(obj) == ExprList:
            code = ''
            for item in obj.exprs[:-1]:
                code += compile_obj(item, root=True) + '\n'
            code += compile_obj(obj.exprs[-1], root=root)
            return code
        elif type(obj) == ID and obj.name == '__func__':
            current_string += 1
            return '\n"' + current_function + '" ___s' + str(current_string) + '\n&___s' + str(current_string)
        # новая функция
        elif type(obj) == FuncDef:
            code = ''
            
            savedvariables = variables.copy()
            savedarrays = arrays.copy()
            savedstructures = structures.copy()
            savedstructuresnoptrs = structuresnoptrs.copy()
            savedunionlist = unionlist.copy()
            savedenumerators = enumerators.copy()
            savedtypedefs = typedefs.copy()
            
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
                
                code += obj.decl.name + ': {___function}\n'
                
                try:
                    i = 0
                    for param in obj.decl.type.args.params:
                        if type(param) == EllipsisParam:
                            funcfixed[obj.decl.name] = i
                            code += create_var('___vargs', 126)
                            break
                        code += compile_obj(param) + '\n'
                        if not param.name in structuresnoptrs:
                            code += get_var(param.name) + ' =\n'
                        else:
                            for j in range(get_struct_length(structs[structures[param.name]])):
                                code += 'dup ' + str(j) + ' + . {' + param.name + '} ' + str(j) + ' + =\n'
                            code += 'drop\n'
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
            
            variables = savedvariables
            arrays = savedarrays
            structures = savedstructures
            structuresnoptrs = savedstructuresnoptrs
            unionlist = savedunionlist
            enumerators = savedenumerators
            typedefs = savedtypedefs
            
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
        # структура
        elif type(obj) == Decl and type(obj.type) == TypeDecl and type(obj.type.type) == Struct:
            name = (obj.type.type.name if obj.type.type.name != None else obj.name + '__STRUCT')
            
            if obj.type.type.name != None and obj.type.type.decls != None:
                structs[obj.type.type.name] = obj.type.type.decls
            
            structures[obj.name] = name
            structuresnoptrs[obj.name] = name
            if obj.type.type.name == None:
                structs[name] = obj.type.type.decls
            
            code = ''
            
            code += '/alloc ' + obj.name + '[' + str(get_struct_length(structs[name])) + ']\n'
            
            if obj.init != None and type(obj.init) == InitList:
                for i in range(len(obj.init.exprs)):
                    expr = obj.init.exprs[i]
                    saved_i = i
                    if type(expr) == NamedInitializer:
                        i = 0
                        for decl in structs[name]:
                            if decl.name == expr.name[0].name:
                                break
                            i += 1
                    
                    code += compile_obj(expr) + ' {' + obj.name + '} ' + ((str(i) + ' + ') if i != 0 else '') + '=\n'
                    
                    if type(expr) == NamedInitializer:
                        i = saved_i
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
        elif type(obj) == Decl and type(obj.type) == TypeDecl and type(obj.type.type) == Union:
            name = (obj.type.type.name if obj.type.type.name != None else obj.name + '__UNION')
            unionlist[obj.name] = name
            if obj.type.type.name == None:
                unions[name] = obj.type.type.decls
        # указатель на объединение
        elif type(obj) == Decl and type(obj.type) == PtrDecl and type(obj.type.type) == TypeDecl and type(obj.type.type.type) == Union:
            unionlist[obj.name] = obj.type.type.type.name
            
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
            code = compile_obj(obj.rvalue) + '\n'
            for i in range(get_struct_length(structs[structures[obj.lvalue.name]])):
                code += 'dup ' + str(i) + ' + . ' + compile_obj(obj.lvalue) + ' ' \
                + str(i) + ' + =\n'
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
        elif type(obj) == Decl and type(obj.type) == ArrayDecl and type(obj.type.type) == TypeDecl and type(obj.type.type.type) == Struct:
            name = (obj.type.type.type.name if obj.type.type.type.name != None else obj.name + '__STRUCT')
            
            if obj.type.type.type.name != None and obj.type.type.type.decls != None:
                structs[obj.type.type.type.name] = obj.type.type.type.decls
            
            structures[obj.name] = name
            structuresnoptrs[obj.name] = name
            if obj.type.type.type.name == None:
                structs[name] = obj.type.type.type.decls
            
            return '/alloc ' + obj.name + '[' + str(get_struct_length(structs[name]) * static_int(obj.type.dim)) + ']\n'
        elif type(obj) == Decl and type(obj.type) == ArrayDecl and (obj.type.dim != None or obj.init != None):
            code = create_var(obj.name, (static_int(obj.type.dim) if obj.type.dim != None else \
              (len(obj.init.exprs) if type(obj.init) == InitList else len(preprocess_string(obj.init.value)) + 1))) + '\n'
            
            if obj.init != None and type(obj.init) == InitList:
                code += get_var(obj.name) + ' 0 ' + get_var(obj.name)[:-1] + '.length}' + ' memset\n'
                for i in range(len(obj.init.exprs)):
                    code += compile_obj(obj.init.exprs[i]) + ' (' + get_var(obj.name) + ' ' \
                    + (str(i) if type(obj.init.exprs[i]) != NamedInitializer else compile_obj(obj.init.exprs[i].name[0])) \
                    + ' +) =\n'
            
            elif obj.init != None and type(obj.init) == Constant:
                for i in range(len(preprocess_string(obj.init.value))):
                    code += str(ord(preprocess_string(obj.init.value)[i])) + ' (' + get_var(obj.name) + ' ' + str(i) + ' +) =\n'
                code += '0 (' + get_var(obj.name) + ' ' + str(len(preprocess_string(obj.init.value))) + ' +) =\n'
            
            # если массив является двумерным
            if type(obj.type.type) == ArrayDecl:
                for i in range(static_int(obj.type.dim)):
                    code += create_var(obj.name + '__A_' + str(i), static_int(obj.type.type.dim)) \
                        + get_var(obj.name + '__A_' + str(i)) + ' ' \
                        + (get_var(obj.name) + ' ' + str(i) + ' +') \
                        + ' =\n'
            return code
        elif type(obj) == Decl and (current_function != '' and current_function != 'main') and not 'static' in obj.storage:
            if type(obj.type) == PtrDecl and type(obj.type.type) == TypeDecl and type(obj.type.type.type) == Struct:
                name = (obj.type.type.type.name if obj.type.type.type.name != None else obj.name + '__STRUCT')
                
                if obj.type.type.type.name != None and obj.type.type.type.decls != None:
                    structs[obj.type.type.type.name] = obj.type.type.type.decls
                
                structures[obj.name] = name
                if obj.type.type.type.name == None:
                    structs[name] = obj.type.type.type.decls
                
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
            if type(obj.type) == PtrDecl and type(obj.type.type) == TypeDecl and type(obj.type.type.type) == Struct:
                name = (obj.type.type.type.name if obj.type.type.type.name != None else obj.name + '__STRUCT')
                
                if obj.type.type.type.name != None and obj.type.type.type.decls != None:
                    structs[obj.type.type.type.name] = obj.type.type.type.decls
                
                structures[obj.name] = name
                if obj.type.type.type.name == None:
                    structs[name] = obj.type.type.type.decls
                
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
            return compile_obj(obj.name) + ' ' + compile_obj(obj.subscript) \
            + ((' ' + str(get_struct_length(structs[structures[obj.name.name]])) + ' *') if type(obj.name) == ID and \
            obj.name.name in structures else '') + ' + .'
        # sizeof
        elif type(obj) == UnaryOp and obj.op == 'sizeof' and type(obj.expr) == ID and is_array(obj.expr.name):
            return get_var(obj.expr.name)[:-1] + '.length}'
        elif type(obj) == UnaryOp and obj.op == 'sizeof' and type(obj.expr) == Typename and \
        type(obj.expr.type) == TypeDecl and type(obj.expr.type.type) == Struct and \
        obj.expr.type.type.name in structs:
            return str(get_struct_length(structs[obj.expr.type.type.name]))
        elif type(obj) == UnaryOp and obj.op == 'sizeof' and type(obj.expr) == StructRef:
            for decl in structs[structures[obj.expr.name.name]]:
                if decl.name == obj.expr.field.name:
                    if type(decl.type) == ArrayDecl:
                        return str(static_int(decl.type.dim))
                    else:
                        return '1'
            return '0'
        elif type(obj) == UnaryOp and obj.op == 'sizeof' and type(obj.expr) == ID and obj.expr.name in structuresnoptrs:
            return str(get_struct_length(structs[structures[obj.expr.name]]))
        elif type(obj) == UnaryOp and obj.op == 'sizeof' and type(obj.expr) == UnaryOp and obj.expr.op == '*' and type(obj.expr.expr) == ID and obj.expr.expr.name in structures and not obj.expr.expr.name in structuresnoptrs:
            return str(get_struct_length(structs[structures[obj.expr.expr.name]]))
        elif type(obj) == UnaryOp and obj.op == 'sizeof' and type(obj.expr) == ArrayRef and type(obj.expr.name) == ID and obj.expr.name.name in structures and not obj.expr.name.name in structuresnoptrs:
            return str(get_struct_length(structs[structures[obj.expr.name.name]]))
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
        elif type(obj) == StructRef and type(obj.name) == ID and obj.name.name in unionlist:
            return '{' + obj.name.name + '} ' + ('.' if obj.type == '.' else ' ')
        elif type(obj) == StructRef:
            i = 0
            j = 0
            struct = get_struct(obj.name)
            
            while struct[j].name != obj.field.name:
                struct[j].type = preprocess_typedefs(struct[j].type)
                if type(struct[j].type) == ArrayDecl:
                    i += static_int(struct[j].type.dim)
                elif type(struct[j].type) == TypeDecl and type(struct[j].type.type) == Struct:
                    for d in structs[struct[j].type.type.name]:
                        if type(d.type) == ArrayDecl:
                            i += static_int(d.type.dim)
                        else:
                            i += 1
                else:
                    i += 1
                j += 1
            
            return compile_obj(obj.name)[:(-2 if obj.type == '.' else None)] + ' ' + ((str(i) + ' + ') if i != 0 else '') \
            + ('.' if type(struct[j].type) != ArrayDecl else ' ')
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
        elif type(obj) == ID and (obj.name in structuresnoptrs or is_array(obj.name)):
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
            
            for item in (obj.stmt.block_items if type(obj.stmt) == Compound else [obj.stmt]):
                if type(item) == Case:
                    code += 'dup ' + compile_obj(item.expr) + ' =? ~___switchl' + str(saved) + '_' + str(i) + ' then\n'
                elif type(item) != Default:
                    code += compile_obj(item) + '\n'
                i += 1
            code += 'drop\n'
            i = 0
            
            for item in (obj.stmt.block_items if type(obj.stmt) == Compound else [obj.stmt]):
                if type(item) == Default:
                    code += '~___switchl' + str(saved) + '_' + str(i) + ' goto\n'
                
                i += 1
            
            code += '~___endswitchl' + str(saved) + ' goto\n'
            
            i = 0
            
            for item in (obj.stmt.block_items if type(obj.stmt) == Compound else [obj.stmt]):
                code += '___switchl' + str(saved) + '_' + str(i) + ':\n'
                try:
                    for o in item.stmts:
                        current_break = '___endswitchl' + str(saved)
                        code += '\t' + compile_obj(o, root=True) + '\n'
                except Exception:
                    ''
                
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
        elif type(obj) == EmptyStatement:
            return ''
        else:
            return '# (unknown) #\n'
    except Exception as e:
        #raise e
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

