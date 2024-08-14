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
    if type(op) == UnaryOp and op.op == '!':
        return compile_cond(op.expr) + ' !'
    elif type(op) != UnaryOp and type(op) != BinaryOp:
        return compile_obj(op) # 1 = true
    
    elif op.op == '==':
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

current_string = -1
# компиляция числа, переменной и т. д.
def compile_obj(obj):
    global current_string
    global current_function
    global variables
    global functions
    global current_if
    global current_while
    global current_for
    global current_switchl
    
    if type(obj) == ExprList:
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
            if len(functions) == 0:
                code += '~main goto\n'
            
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
                code += '~' + obj.decl.name + '.___start create_thrd1 0 {return} thrd_1 ' + obj.decl.name + '.___start:\n'
            
        
        if obj.body.block_items != None:
            for item in obj.body.block_items:
                code += compile_obj(item) + '\n'
        
        if type(obj.decl.type.type) != PtrDecl and obj.decl.type.type.type.names[0].startswith('__thr'):
            code += '\nhalt thrd_0\n'
        else:
            code += '\n' + compile_obj(Return(Constant('int', '0')))
        
        current_function = ''
        
        return code
    # присваивание
    elif type(obj) == Assignment and obj.op == '=':
        return compile_obj(obj.rvalue) + ' ' + (compile_obj(obj.lvalue)[:-2] if type(obj.lvalue) == ArrayRef else get_var(obj.lvalue.name)) + ' = ' + (compile_obj(obj.lvalue)[:-2] if type(obj.lvalue) == ArrayRef else get_var(obj.lvalue.name)) + ' .'
    elif type(obj) == Assignment and obj.op[0] in '+-/*^%|&' and obj.op.endswith('='):
        return '(' + compile_obj(obj.rvalue) + ' ' + compile_obj(obj.lvalue).replace('!', '') + ' . ' + obj.op[0].replace('%', 'mod').replace('&', 'and') + ') ' + (compile_obj(obj.lvalue)[:-2] if type(obj.lvalue) == ArrayRef else get_var(obj.lvalue.name)) + ' = ' + (compile_obj(obj.lvalue)[:-2] if type(obj.lvalue) == ArrayRef else get_var(obj.lvalue.name)) + ' .'
    # сложение, вычитание и др.
    elif type(obj) == BinaryOp and obj.op in '-+/*^|':
        return compile_obj(obj.left) + ' ' + compile_obj(obj.right) + ' ' + obj.op
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
                code += '\t' + compile_obj(item) + '\n'
        else:
            code += '\t' + compile_obj(obj.iftrue) + '\n'
        
        code += '~___endif' + str(saved) + ' goto ___else' + str(saved) + ': ' + (';' if current_function == 'main' else '') + '\n'
        
        if obj.iffalse != None and type(obj.iffalse) == Compound:
            for item in obj.iffalse.block_items:
                code += compile_obj(item) + '\n'
        elif obj.iffalse != None:
            code += compile_obj(obj.iffalse) + '\n'
        
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
    elif type(obj) == Decl and type(obj.type) == ArrayDecl:
        return create_var(obj.name + '__ARRAY__', int(obj.type.dim.value)) \
            + create_var(obj.name) \
            + get_var(obj.name + '__ARRAY__') + ' ' + get_var(obj.name) + ' ='
    elif type(obj) == Decl and (current_function != '' and current_function != 'main') and not 'static' in obj.storage:
        code = ''
        variables += [current_function + '.' + obj.name]
        code += '/alloc ' + current_function + '.' + obj.name + '___ARRAY__[64]\n'
        code += '/define ' + current_function + '.' + obj.name + ' :{' \
            + current_function + '.' + obj.name + '___ARRAY__} {__retptr}! +' + '\n'
        if obj.init != None:
            code += compile_obj(Assignment('=', ID(current_function + '.' + obj.name), obj.init)) + '\n'
        
        return code
    elif type(obj) == Decl:
        code = ''
        code += create_var(obj.name)
        if obj.init != None:
            code += compile_obj(Assignment('=', ID(obj.name), obj.init)) + '\n'
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
        return get_var(obj.name.name) + ' . ' + compile_obj(obj.subscript) + ' + .'
    # sizeof(массив)
    elif type(obj) == UnaryOp and obj.op == 'sizeof' and type(obj.expr) == ID:
        return get_var(obj.expr.name)[:-1] + '__ARRAY__.length}'
    # sizeof
    elif type(obj) == UnaryOp and obj.op == 'sizeof':
        return '1'
    # -выражение
    elif type(obj) == UnaryOp and obj.op == '-':
        return compile_obj(obj.expr) + ' neg'
    # ~выражение
    elif type(obj) == UnaryOp and obj.op == '~':
        return compile_obj(obj.expr) + ' neg --'
    # переменная
    elif type(obj) == ID:
        return get_var(obj.name) + ' .'
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
            elif s_format[i] == '%' and s_format[i + 1] == 'd':
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
        return '(' + get_var(obj.expr.name) + ' . ++) ' + get_var(obj.expr.name) + ' = ' + get_var(obj.expr.name) + ' .'
    elif type(obj) == UnaryOp and obj.op == '--' and type(obj.expr) == ID:
        return '(' + get_var(obj.expr.name) + ' . --) ' + get_var(obj.expr.name) + ' = ' + get_var(obj.expr.name) + ' .'
    elif type(obj) == UnaryOp and obj.op == 'p++' and type(obj.expr) == ID:
        return get_var(obj.expr.name) + ' . (' + get_var(obj.expr.name) + ' . ++) ' + get_var(obj.expr.name) + ' ='
    elif type(obj) == UnaryOp and obj.op == 'p--' and type(obj.expr) == ID:
        return get_var(obj.expr.name) + ' . (' + get_var(obj.expr.name) + ' . --) ' + get_var(obj.expr.name) + ' ='
    
    elif type(obj) == UnaryOp and obj.op == '++' and type(obj.expr) == ArrayRef:
        return '(' + compile_obj(obj.expr) + ' ++) ' + compile_obj(obj.expr)[:-2] + ' = ' + compile_obj(obj.expr)
    elif type(obj) == UnaryOp and obj.op == '--' and type(obj.expr) == ArrayRef:
        return '(' + compile_obj(obj.expr) + ' --) ' + compile_obj(obj.expr)[:-2] + ' = ' + compile_obj(obj.expr)
    elif type(obj) == UnaryOp and obj.op == 'p++' and type(obj.expr) == ArrayRef:
        return compile_obj(obj.expr) + ' (' + compile_obj(obj.expr) + ' ++) ' + compile_obj(obj.expr)[:-2] + ' ='
    elif type(obj) == UnaryOp and obj.op == 'p--' and type(obj.expr) == ArrayRef:
        return compile_obj(obj.expr) + ' (' + compile_obj(obj.expr) + ' --) ' + compile_obj(obj.expr)[:-2] + ' ='
    # получение адреса переменной/массива
    elif type(obj) == UnaryOp and obj.op == '&' and type(obj.expr) == ID:
        return get_var(obj.expr.name)
    # while
    elif type(obj) == While:
        code = ''
        saved = current_while
        current_while += 1
        code += '___while' + str(saved) + ': ' + compile_cond(obj.cond)
        
        code += ' ~___endwhile' + str(saved) + ' else ' + (';' if current_function == 'main' else '') + '\n'
        
        if type(obj.stmt) == Compound:
            for item in obj.stmt.block_items:
                if type(item) == Continue:
                    code += '\t' + '~___while' + str(saved) + ' goto\n'
                elif type(item) == Break:
                    code += '\t' + '~___endwhile' + str(saved) + ' goto\n'
                else:
                    code += '\t' + compile_obj(item) + '\n'
        else:
            code += '\t' + compile_obj(obj.stmt) + '\n'
        
        code += '~___while' + str(saved) + ' goto ___endwhile' + str(saved) + ':'
        
        return code
    # do-while
    elif type(obj) == DoWhile:
        code = ''
        saved = current_while
        current_while += 1
        code += '___dowhile' + str(saved) + ':\n'
        
        if type(obj.stmt) == Compound:
            for item in obj.stmt.block_items:
                if type(item) == Continue:
                    code += '\t' + '~___dowhile' + str(saved) + ' goto\n'
                elif type(item) == Break:
                    code += '\t' + '~___enddowhile' + str(saved) + ' goto\n'
                else:
                    code += '\t' + compile_obj(item) + '\n'
        else:
            code += '\t' + compile_obj(obj.stmt) + '\n'
        
        code += compile_cond(obj.cond) + ' ~___dowhile' + str(saved) + ' then ___enddowhile' + str(saved) + ':\n'
        
        return code
    # for
    elif type(obj) == For:
        code = ''
        saved = current_for
        current_for += 1
        code += compile_obj(obj.init) + ' '
        code += '___for' + str(saved) + ': ' + compile_cond(obj.cond)
        
        code += ' ~___endfor' + str(saved) + ' else ' + (';' if current_function == 'main' else '') + '\n'
        
        if type(obj.stmt) == Compound:
            for item in obj.stmt.block_items:
                if type(item) == Continue:
                    code += '\t' + compile_obj(obj.next) + ' ~___for' + str(saved) + ' goto\n'
                elif type(item) == Break:
                    code += '\t' + '~___endfor' + str(saved) + ' goto\n'
                else:
                    code += '\t' + compile_obj(item) + '\n'
        else:
            code += '\t' + compile_obj(obj.stmt) + '\n'
        
        code += compile_obj(obj.next) + ' ~___for' + str(saved) + ' goto ___endfor' + str(saved) + ':'
        
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
                code += '\t' + compile_obj(o) + '\n'
            
            code += '~___endcase' + str(saved) + ' goto ___switchl' + str(current_switchl) + ': ' + (';' if current_function == 'main' else '') + '\n'
            
            current_switchl += 1
        code += '___switchl' + str(current_switchl - 1) + ':\n'
        code += '___endcase' + str(saved) + ':\n'
        
        return code
    ####################
    elif type(obj) == EmptyStatement:
        return ''
    else:
        return '# (unknown) #\n'

################################################################################

if __name__ == '__main__':
    import sys
    from pycparser import parse_file
    
    if len(sys.argv) == 1:
        print('usage: ./c2xcc.py FILE ["CPP_ARGS"] [> OUT_FILE]')
        sys.exit(1)
    
    ast = parse_file(sys.argv[1], use_cpp=True, cpp_args=('' if len(sys.argv) < 3 else sys.argv[2]))
    
    print(get_init_code())
    for item in ast:
        print(compile_obj(item))

