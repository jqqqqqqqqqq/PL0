# -*- coding: utf-8 -*-
import const


const.amax = 2147483647  # 最打允许
const.levmax = 3  # 最大嵌套层数
const.cxmax = 2000  # 代码数组的长度
const.stacksize = 1000  # 数据栈大小
const.nul = 0x1  # 空
const.ident = 0x2  # 标识符
const.number = 0x4  # 数值
const.plus = 0x8  # +
const.minus = 0x10  # -
const.times = 0x20  # *
const.slash = 0x40  # /
const.oddsym = 0x80  # 奇数判断
const.eql = 0x100  # =
const.neq = 0x200  # <>
const.lss = 0x400  # <
const.leq = 0x800  # <=
const.gtr = 0x1000  # >
const.geq = 0x2000  # >=
const.lparen = 0x4000  # (
const.rparen = 0x8000  # )
const.comma = 0x10000  # ,
const.semicolon = 0x20000  # ;
const.period = 0x40000  # .
const.becomes = 0x80000  # :=
const.beginsym = 0x100000  # 保留字：begin
const.endsym = 0x200000  # 保留字：end
const.ifsym = 0x400000  # 保留字：if
const.thensym = 0x800000  # 保留字：then
const.whilesym = 0x1000000  # 保留字：while
const.dosym = 0x2000000  # 保留字：do
const.callsym = 0x4000000  # 保留字：call
const.constsym = 0x8000000  # 保留字：const
const.varsym = 0x10000000  # 保留字：var
const.procsym = 0x20000000  # 保留字：procedure
const.readsym = 0x40000000
const.writesym = 0x80000000
const.elsesym = 0x100000000
const.repeatsym = 0x200000000
const.untilsym = 0x400000000

const.declare_begin_sys = const.constsym | const.varsym | const.procsym  # 声明开始集合 declbegsys
const.statement_begin_sys = const.beginsym | const.callsym | const.ifsym | const.whilesym  # 表达式开始集合 statbegsys
const.factor_begin_sys = const.ident | const.number | const.lparen  # factor开始符号集合 facbegsys


object_type = {'constant': 0, 'variable': 1, 'procedure': 2}
p_code = {'LIT': 0, 'OPR': 1, 'LOD': 2, 'STO': 3, 'CAL': 4, 'INT': 5, 'JMP': 6, 'JPC': 7}
p_code_rev = {0: 'LIT', 1: 'OPR', 2: 'LOD', 3: 'STO', 4: 'CAL', 5: 'INT', 6: 'JMP', 7: 'JPC'}
# lit 0, a : load constant a
# opr 0, a : execute operation a
# lod l, a : load variable l, a
# sto l, a : store variable l, a
# cal l, a : call procedure a at level l
# Int 0, a : increment t-register by a
# jmp 0, a : jump to a
# jpc 0, a : jump conditional to a when stack top is 0, and --t
# jp0 0, a : jump conditional to a when stack top is 0
# jp1 0, a : jump conditional to a when stack top is 1


class Instruction:
    f = 0  # function_code
    l = 0  # level
    a = 0  # displacement_address

    def __init__(self, f, l, a):
        self.f = f
        self.l = l
        self.a = a
        return

error_message = (
"""  0 """    "",
"""  1 """    "Found ':=' when expecting '='.",
"""  2 """    "There must be a number to follow '='.",
"""  3 """    "There must be an '=' to follow the identifier.",
"""  4 """    "There must be an identifier to follow 'const', 'var', or 'procedure'.",
"""  5 """    "Missing ',' or ';'.",
"""  6 """    "Incorrect procedure name.",
"""  7 """    "Statement expected.",
"""  8 """    "Follow the statement is an incorrect symbol.",
"""  9 """    "'.' expected.",
""" 10 """    "';' expected.",
""" 11 """    "Undeclared identifier.",
""" 12 """    "Illegal assignment.",
""" 13 """    "':=' expected.",
""" 14 """    "There must be an identifier to follow the 'call'.",
""" 15 """    "A constant or variable can not be called.",
""" 16 """    "'then' expected.",
""" 17 """    "';' or 'end' expected.",
""" 18 """    "'do' expected.",
""" 19 """    "Incorrect symbol.",
""" 20 """    "Relative operators expected.",
""" 21 """    "Procedure identifier can not be in an expression.",
""" 22 """    "Missing ')'.",
""" 23 """    "The symbol can not be followed by a factor.",
""" 24 """    "The symbol can not be as the beginning of an expression.",
""" 25 """    "",
""" 26 """    "",
""" 27 """    "",
""" 28 """    "",
""" 29 """    "",
""" 30 """    "",
""" 31 """    "The number is too great.",
""" 32 """    "There are too many levels.",
""" 33 """    "There should be a right paren.",
""" 34 """    "There should be a left paren.")


class Table:
    name = ''
    kind = 0
    value = 0
    level = 0
    address = 0

    def __init__(self):
        return

word = {  # 保留字对应的symbol类型表
    "begin": 0x100000,
    "call": 0x4000000,
    "const": 0x8000000,
    "do": 0x2000000,
    "end": 0x200000,
    "if": 0x400000,
    "odd": 0x80,
    "procedure": 0x20000000,
    "then": 0x800000,
    "var": 0x10000000,
    "while": 0x1000000,
    "read": 0x40000000,
    "write": 0x80000000,
    "else": 0x100000000,
    "repeat": 0x200000000,
    "until": 0x400000000
}

ssym = {  # 符号对应的symbol类型表
    '+': 0x8,
    '-': 0x10,
    '*': 0x20,
    '/': 0x40,
    '(': 0x4000,
    ')': 0x8000,
    '=': 0x100,
    ',': 0x10000,
    '.': 0x40000,
    ';': 0x20000,
}


reflect = {
    "ident": 0x2,  # 标识符
    "number": 0x4,  # 数值
    "plus": 0x8,  # +
    "minus": 0x10,  # -
    "times": 0x20,  # *
    "slash": 0x40,  # /
    "oddsym": 0x80,  # 奇数判断
    "eql": 0x100,  # =
    "neq": 0x200,  # <>
    "lss": 0x400,  # <
    "leq": 0x800,  # <=
    "gtr": 0x1000,  # >
    "geq": 0x2000,  # >=
    "lparen": 0x4000,  # (
    "rparen": 0x8000,  # )
    "comma": 0x10000,  # ,
    "semicolon": 0x20000,  # ;
    "period": 0x40000,  # .
    "becomes": 0x80000,  # :=
    "beginsym": 0x100000,  # 保留字：begin
    "endsym": 0x200000,  # 保留字：end
    "ifsym": 0x400000,  # 保留字：if
    "thensym": 0x800000,  # 保留字：then
    "whilesym": 0x1000000,  # 保留字：while
    "dosym": 0x2000000,  # 保留字：do
    "callsym": 0x4000000,  # 保留字：call
    "constsym": 0x8000000,  # 保留字：const
    "varsym": 0x10000000,  # 保留字：var
    "procsym": 0x20000000,  # 保留字：procedure
    "readsym": 0x40000000,
    "writesym": 0x80000000,
    "elsesym": 0x100000000,
    "repeatsym": 0x200000000,
    "untilsym": 0x400000000
}