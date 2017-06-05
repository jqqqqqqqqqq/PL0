# -*- coding: utf-8 -*-

import define

char = ' '  # 最后一次读出来的字符 ch
sym = 0  # 最后一次是别的token类型 sym
id = ''  # 最后一次识别出的标识符 id
number = 0  # 最后一次识别出的数字 num
char_count = 0  # 字母计数 cc
line_number = 0  # 行号
errors = 0
cx = 0  # 代码分配指针 cx
a = ''  # 正在分析的词 a
code = []  # 指令表 code
file_content = []  # 文本内容
dx = 0  # 数据分配指针
lev = 0  # 当前的块深度
tx = 0  # 当前的符号表指针
stack = []  # 数据栈
table = [define.Table()]  # 符号表