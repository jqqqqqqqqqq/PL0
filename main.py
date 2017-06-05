# -*- coding: utf-8 -*-

import define
import var
import const
import sys
import config


def invert_dict(d):
    return dict((v, k) for k, v in d.iteritems())


def get_fsys(a):
    result = []
    for k, v in define.reflect.iteritems():
        print a & v
        if a & v > 0:
            result.append(k)
    return result


def error(n):
    print 'Error:' + ' '*n,
    print str(n) + ': ' + define.error_message[n]
    var.errors += 1


def trim():
    while len(var.file_content[var.line_number]) == 0:
        print str(var.cx).ljust(6, ' ')
        var.line_number += 1
        if var.line_number == len(var.file_content):
            print ""
            print "Error: program incomplete"
            exit(1)


def getCh():
    trim()
    if var.char_count == len(var.file_content[var.line_number]):
        var.char_count = 0
        var.line_number += 1
        if var.line_number == len(var.file_content):
            print ""
            print "Error: program incomplete"
            exit(1)
        trim()
        if config.SHOW_PL0_LINE_NUMBER:
            print str(var.cx).ljust(6, ' '),
        for c in var.file_content[var.line_number]:
            sys.stdout.write(c)
        print ''

    var.char = var.file_content[var.line_number][var.char_count]
    var.char_count += 1


def getsym():
    while var.char == ' ' or var.char == '\t':
        getCh()
    if var.char.isalpha():
        var.a = var.char
        getCh()
        while var.char.isalpha() or var.char.isdigit():
            var.a += var.char
            getCh()
        var.id = var.a
        var.sym = 0
        for (k, v) in define.word.items():
            if k == var.id:
                var.sym = v
        if var.sym == 0:
            var.sym = const.ident
    elif var.char.isdigit():
        var.sym = const.number
        var.number = 0
        while True:
            var.number = var.number * 10 + int(var.char)
            getCh()
            if not var.char.isdigit():
                break
        if var.number > 2147483647:
            var.number = 0
            error(31)
    elif var.char == ':':
        getCh()
        if var.char == '=':
            var.sym = const.becomes
            getCh()
        else:
            var.sym = const.nul
    elif var.char == '<':
        getCh()
        if var.char == '=':
            var.sym = const.leq
            getCh()
        elif var.char == '>':
            var.sym = const.neq
            getCh()
        else:
            var.sym = const.lss
    elif var.char == '>':
        getCh()
        if var.char == '=':
            var.sym = const.geq
            getCh()
        else:
            var.sym = const.gtr
    else:
        var.sym = const.nul
        for (k, v) in define.ssym.items():
            if var.char == k:
                var.sym = v
                break
        getCh()


# 中间代码生成，将生成的中间代码写入中间代码数组，供后面解释器运行
def gen(x, y, z):
    if var.cx > const.cxmax:  # cx = len(var.code)
        print "program too long"
        exit(1)
    var.code.append(define.Instruction(x, y, z))
    var.cx += 1
    if config.SHOW_INSTANT_TRANSLATION:
        list_code(var.cx - 1)


# 测试当前单词是否合法
# s1:当语法分析进入或退出某一语法单元时当前单词符合应属于的集合
# s2:在某一出错状态下，可恢复语法分析正常工作的补充单词补给
# n:出错信息编号，当当前符号不属于合法的s1集合时发出的错误信息
def test(s1, s2, n):
    if not var.sym & s1:
        error(n)
        s1 = s1 | s2
        while not var.sym & s1:
            getsym()


# 符号表
def enter(k):
    var.tx += 1
    table = define.Table()
    table.name = var.id
    table.kind = k

    # Python没有Switch，强行用Dict解决
    def constant():
        if var.number > const.amax:
            error(31)
            var.number = 0
        table.value = var.number

    def variable():
        table.level = var.lev
        table.address = var.dx
        var.dx += 1

    def procedure():
        table.level = var.lev

    {  # object_type = {'constant': 0, 'variable': 1, 'procedure': 2}
        define.object_type['constant']: constant,
        define.object_type['variable']: variable,
        define.object_type['procedure']: procedure
    }.get(k)()
    var.table.append(table)


# 查找符号在符号表中的位置
def position(id):
    for index, table in enumerate(reversed(var.table)):
        if id == table.name:
            return len(var.table) - index - 1
    return 0


# 常量声明
def const_declaration():
    if var.sym == const.ident:
        getsym()
        if var.sym == const.eql or var.sym == const.becomes:
            if var.sym == const.becomes:
                error(1)
            getsym()
            if var.sym == const.number:
                enter(define.object_type['constant'])
                getsym()
            else:
                error(2)
        else:
            error(3)
    else:
        error(4)


# 变量声明
def var_declaration():
    if var.sym == const.ident:
        enter(define.object_type['variable'])
        getsym()
    else:
        error(4)


# 输出当前代码块的中间代码
def list_code(cx0):
    for i in range(cx0, var.cx):
        if config.SHOW_P_CODE_LINE_NUMBER:
            print str(i).ljust(10),
        print define.p_code_rev[var.code[i].f] + ' ' \
            + str(var.code[i].l) + ' ' + str(var.code[i].a)


# factor处理，fsys为出错可用于恢复语法的符号集合
def factor(fsys):
    test(const.factor_begin_sys, fsys, 24)
    while var.sym & const.factor_begin_sys:
        if var.sym == const.ident:
            i = position(var.id)
            if i == 0:
                error(11)
            else:
                def constant():
                    gen(define.p_code['LIT'], 0, var.table[i].value)

                def variable():
                    gen(define.p_code['LOD'], var.lev - var.table[i].level, var.table[i].address)

                def procedure():
                    error(21)

                {
                    define.object_type['constant']: constant,
                    define.object_type['variable']: variable,
                    define.object_type['procedure']: procedure
                }.get(var.table[i].kind)()
            getsym()
        elif var.sym == const.number:
            if var.number > 2147483647:
                error(31)
                var.number = 0
            gen(define.p_code['LIT'], 0, var.number)
            getsym()
        elif var.sym == const.lparen:
            getsym()
            expression(const.rparen | fsys)
            if var.sym == const.rparen:
                getsym()
            else:
                error(22)
            test(fsys, const.lparen, 23)


# term处理
def term(fsys):
    factor(fsys | const.times | const.slash)
    while var.sym == const.times or var.sym == const.slash:
        mulop = var.sym
        getsym()
        factor(fsys | const.times | const.slash)
        if mulop == const.times:
            gen(define.p_code['OPR'], 0, 4)
        else:
            gen(define.p_code['OPR'], 0, 5)


# expression处理
def expression(fsys):
    if var.sym == const.plus or var.sym == const.minus:
        addop = var.sym
        getsym()
        term(fsys | const.plus | const.minus)
        if addop == const.minus:
            gen(define.p_code['OPR'], 0, 1)
    else:
        term(fsys | const.plus | const.minus)
    while var.sym == const.plus or var.sym == const.minus:
        addop = var.sym
        getsym()
        term(fsys | const.plus | const.minus)
        if addop == const.plus:
            gen(define.p_code['OPR'], 0, 2)
        else:
            gen(define.p_code['OPR'], 0, 3)


# condition处理
def condition(fsys):
    if var.sym == const.oddsym:
        getsym()
        expression(fsys)
        gen(define.p_code['OPR'], 0, 6)
    else:
        expression(fsys | const.eql | const.neq | const.lss | const.gtr | const.leq | const.geq)
        if not var.sym & (const.eql | const.neq | const.lss | const.gtr | const.leq | const.geq):
            error(20)
        else:
            relop = var.sym
            getsym()
            expression(fsys)
            gen(define.p_code['OPR'], 0, {
                const.eql: 8,
                const.neq: 9,
                const.lss: 10,
                const.geq: 11,
                const.gtr: 12,
                const.leq: 13}[relop])


# statement处理
def statement(fsys):
    if var.sym == const.ident:
        i = position(var.id)
        if i == 0:
            error(11)
        elif var.table[i].kind != define.object_type['variable']:
            error(12)
            i = 0
        getsym()
        if var.sym == const.becomes:
            getsym()
        else:
            error(13)
        expression(fsys)
        if i != 0:
            gen(define.p_code['STO'], var.lev - var.table[i].level, var.table[i].address)
    elif var.sym == const.readsym:
        getsym()
        if var.sym != const.lparen:
            error(34)
        else:
            while True:
                getsym()
                if var.sym == const.ident:
                    i = position(var.id)
                else:
                    i = 0
                if i == 0:
                    error(11)
                else:
                    gen(define.p_code['OPR'], 0, 16)
                    gen(define.p_code['STO'], var.lev - var.table[i].level, var.table[i].address)
                getsym()
                if not var.sym == const.comma:
                    break
        if var.sym != const.rparen:
            error(33)  # 格式错误，应为右括号
            while not var.sym & fsys:
                getsym()  # 出错补救，直到遇到上层函数的后继符号
        else:
            getsym()
    elif var.sym == const.writesym:
        getsym()
        if var.sym == const.lparen:
            while True:
                getsym()
                expression(fsys | const.rparen | const.comma)
                gen(define.p_code['OPR'], 0, 14)
                gen(define.p_code['OPR'], 0, 15)
                if not var.sym == const.comma:
                    break
            if var.sym != const.rparen:
                error(33)
            else:
                getsym()
    elif var.sym == const.callsym:
        getsym()
        if var.sym != const.ident:
            error(14)
        else:
            i = position(var.id)
            if i == 0:
                error(11)
            elif var.table[i].kind == define.object_type['procedure']:
                gen(define.p_code['CAL'], var.lev - var.table[i].level, var.table[i].address)
            else:
                error(15)
            getsym()
    elif var.sym == const.ifsym:
        getsym()
        condition(fsys | const.thensym | const.dosym)
        if var.sym == const.thensym:
            getsym()
        else:
            error(16)
        cx1 = var.cx
        gen(define.p_code['JPC'], 0, 0)
        statement(fsys)
        if var.sym == const.elsesym:
            getsym()
            cx2 = var.cx
            gen(define.p_code['JMP'], 0, 0)
            var.code[cx1].a = var.cx
            statement(fsys)
            var.code[cx2].a = var.cx
        else:
            var.code[cx1].a = var.cx
    elif var.sym == const.beginsym:
        getsym()
        statement(fsys | const.semicolon | const.endsym)
        while var.sym == const.semicolon or var.sym & const.statement_begin_sys:
            if var.sym == const.semicolon:
                getsym()
            else:
                error(10)
            statement(fsys | const.semicolon | const.endsym)
        if var.sym == const.endsym:
            getsym()
        else:
            error(17)
    elif var.sym == const.whilesym:
        cx1 = var.cx
        getsym()
        condition(fsys | const.dosym)
        cx2 = var.cx
        gen(define.p_code['JPC'], 0, 0)
        if var.sym == const.dosym:
            getsym()
        else:
            error(18)
        statement(fsys)
        gen(define.p_code['JMP'], 0, cx1)
        var.code[cx2].a = var.cx
    elif var.sym == const.repeatsym:
        getsym()
        cx1 = var.cx
        statement(fsys | const.semicolon | const.untilsym)
        while var.sym == const.semicolon or var.sym & const.statement_begin_sys:
            if var.sym == const.semicolon:
                getsym()
            else:
                error(10)
            statement(fsys | const.semicolon | const.untilsym)
        if var.sym == const.untilsym:
            getsym()
        else:
            error(19)
        condition(fsys)
        gen(define.p_code['JPC'], 0, cx1)
    else:
        test(fsys, 0, 19)


# block处理
def block(fsys):  # 地址寄存器 tx0, cx0, tx1, dx1 给出每层局部量当前已分配到的相对位置
    var.dx = 3  # 每一层最开始的位置有三个空间用于存放静态链 SL、动态链 DL 和 返回地址 RA
    tx0 = var.tx
    var.table[var.tx].address = var.cx
    gen(define.p_code['JMP'], 0, 0)
    if var.lev > const.levmax:
        error(32)
    while True:
        if var.sym == const.constsym:
            getsym()
            # while True:
            const_declaration()
            while var.sym == const.comma:
                getsym()
                const_declaration()
            if var.sym == const.semicolon:
                getsym()
            else:
                error(5)
                # if not var.sym == const.ident:
                #     break
        if var.sym == const.varsym:
            getsym()
            # while True:
            var_declaration()
            while var.sym == const.comma:
                getsym()
                var_declaration()
            if var.sym == const.semicolon:
                getsym()
            else:
                error(5)
            #    if not var.sym == const.ident:
            #        break
        while var.sym == const.procsym:
            getsym()
            if var.sym == const.ident:
                enter(define.object_type['procedure'])
                getsym()
            else:
                error(4)
            if var.sym == const.semicolon:
                getsym()
            else:
                error(5)
            var.lev += 1
            tx1 = var.tx
            dx1 = var.dx
            block(fsys | const.semicolon)
            var.lev -= 1
            var.tx = tx1
            var.dx = dx1
            if var.sym == const.semicolon:
                getsym()
                test(const.statement_begin_sys | const.ident | const.procsym, fsys, 6)
            else:
                error(5)
        test(const.statement_begin_sys | const.ident | const.period, const.declare_begin_sys, 7)
        if not var.sym & const.declare_begin_sys:
            break
    var.code[var.table[tx0].address].a = var.cx
    var.table[tx0].address = var.cx
    cx0 = var.cx
    gen(define.p_code['INT'], 0, var.dx)
    statement(fsys | const.semicolon | const.endsym)
    gen(define.p_code['OPR'], 0, 0)  # return
    test(fsys, 0, 8)
    # listcode(cx0)


# 通过静态链求出数据基地址
def base(b, l):
    b1 = b
    while l > 0:
        b1 = var.stack[b1]
        l -= 1
    return b1


# 指令集解释器
def interpret():
    t = 0
    b = 1
    p = 0
    for i in range(0, const.stacksize):
        var.stack.append(0)
    print "start PL/0"
    var.stack[1] = 0  # todo: check if append should be used instead
    var.stack[2] = 0
    var.stack[3] = 0
    while True:
        i = var.code[p]
        p += 1
        if i.f == define.p_code['LIT']:
            t += 1
            var.stack[t] = i.a
        elif i.f == define.p_code['OPR']:
            if i.a == 0:  # 返回
                t = b - 1
                p = var.stack[t + 3]
                b = var.stack[t + 2]
            elif i.a == 1:  # 负号
                var.stack[t] = - var.stack[t]
            elif i.a == 2:  # 加法
                t -= 1
                var.stack[t] = var.stack[t] + var.stack[t + 1]
            elif i.a == 3:  # 减法
                t -= 1
                var.stack[t] = var.stack[t] - var.stack[t + 1]
            elif i.a == 4:  # 乘法
                t -= 1
                var.stack[t] = var.stack[t] * var.stack[t + 1]
            elif i.a == 5:  # 除法
                t -= 1
                var.stack[t] = var.stack[t] / var.stack[t + 1]
            elif i.a == 6:  # odd
                var.stack[t] %= 2
            elif i.a == 8:  # ==
                t -= 1
                var.stack[t] = var.stack[t] == var.stack[t + 1]
            elif i.a == 9:  # !=
                t -= 1
                var.stack[t] = var.stack[t] != var.stack[t + 1]
            elif i.a == 10:  # <
                t -= 1
                var.stack[t] = var.stack[t] < var.stack[t + 1]
            elif i.a == 11:  # >=
                t -= 1
                var.stack[t] = var.stack[t] >= var.stack[t + 1]
            elif i.a == 12:  # >
                t -= 1
                var.stack[t] = var.stack[t] > var.stack[t + 1]
            elif i.a == 13:  # <=
                t -= 1
                var.stack[t] = var.stack[t] <= var.stack[t + 1]
            elif i.a == 14:
                print var.stack[t],
                # todo print to file
                t -= 1
            elif i.a == 15:
                print
                # todo print to file
            elif i.a == 16:
                t += 1
                # todo print to file
                var.stack[t] = int(raw_input('?'))
        elif i.f == define.p_code['LOD']:
            t += 1
            var.stack[t] = var.stack[base(b, i.l) + i.a]
        elif i.f == define.p_code['STO']:
            var.stack[base(b, i.l) + i.a] = var.stack[t]
            # print str(var.stack[t]).ljust(10)
            t -= 1
        elif i.f == define.p_code['CAL']:
            var.stack[t + 1] = base(b, i.l)
            var.stack[t + 2] = b
            var.stack[t + 3] = p
            b = t + 1
            p = i.a
        elif i.f == define.p_code['INT']:
            t += i.a
        elif i.f == define.p_code['JMP']:
            p = i.a
        elif i.f == define.p_code['JPC']:
            if var.stack[t] == 0:
                p = i.a
            t -= 1
        if not p != 0:
            break
    print "end PL/0"


def main():
    infile_address = raw_input("please input your source file name:")
    infile_address = infile_address.strip()
    infile = open(infile_address, "r")
    # infile = open("test.txt", "r")
    if not infile:
        print "file not found"
        exit(1)

    while True:  # 处理规则：一次性读取所有文本，将所有字符拆开，过滤换行，并替换为二维数组的第一个维度
        line = infile.readline()
        if not line:
            break
        line = list(line)
        try:
            line.remove('\n')
            line.remove('\r')
        except ValueError:
            pass
        line.append(' ')
        var.file_content.append(line)

    if config.SHOW_PL0_LINE_NUMBER:
        print str(var.cx).ljust(6, ' '),  # 补充输出第一行
    for c in var.file_content[var.line_number]:
        sys.stdout.write(c)
    print ''

    getsym()
    block(const.declare_begin_sys | const.statement_begin_sys | const.period)
    if var.sym != const.period:
        error(9)
    if var.errors == 0:
        print
        print "p_code:"
        list_code(0)
        if config.AUTOMATIC_EXECUTE:
            print
            print "execute begin:"
            interpret()
    else:
        print "errors in PL/0 program"

if __name__ == '__main__':
    main()


