# -*- coding:utf-8 -*-


import re
from lark import Lark, Transformer

grammar = r"""
?prog : and_clause | or_clause | predicate

and_clause : "AND" "(" prog ("," prog)* ")"
or_clause : "OR" "(" prog ("," prog)* ")"

predicate : set_pred | interval_pred
set_pred : attr op range
!op : "∈" | "∉"
range : "{" value ("," value)* "}"
value : STRING | bool
interval_pred : attr op interval
interval : lhs_op NUMBER "," NUMBER rhs_op
!lhs_op : "(" | "["
!rhs_op : ")" | "]"
!bool : "True"i | "False"i

attr : /\w+/

%import python.STRING -> STRING
%import common.SIGNED_NUMBER -> NUMBER
%import common.WS
%ignore WS
"""


class Visitor(Transformer):
    def STRING(self, string):
        return str(string)[1:-1]

    def NUMBER(self, num):
        return eval(num)

    def attr(self, var):
        return str(var[0])

    def and_clause(self, clauses):
        return {"and": clauses}

    def or_clause(self, clauses):
        return {"or": clauses}

    def predicate(self, pred):
        return pred[0]

    def set_pred(self, pred):
        lhs, op, rhs = pred
        return {op: [lhs, rhs]}

    def op(self, op):
        return "in" if str(op[0]) == "∈" else "nin"

    def interval_pred(self, pred):
        lhs, op, rhs = pred
        return {op: [lhs, rhs]}

    def range(self, values):
        return {"range": values}

    def lhs_op(self, op):
        return str(op[0])

    def rhs_op(self, op):
        return str(op[0])

    def interval(self, interval):
        return {"interval": interval}

    def bool(self, boolean):
        return eval(boolean[0])

    def value(self, v):
        return v[0]


class Parser:
    def __init__(self):
        self.visitor = Visitor()
        self.parser = Lark(grammar, start="prog")

    def parse(self, program):
        program = re.sub(r"Regex\_[\(|\)|\\|\{|\}|,|\w]+", "Regex", program)
        # print(program)
        return self.visitor.transform(self.parser.parse(program))


if __name__ == '__main__':
    prog = 'OR(AND(Color ∉ {"Gray", "Blue", "Red", "Black"}, Type ∉ {"Van", "Sedan"}), AND(Color ∉ {"Gray", "White", "Black"}, Type ∉ {"Hatchback"}), AND(Color ∉ {"Gray", "Blue", "Red", "White"}, Type ∉ {"Suv", "Sedan"}))'
    parser = Parser()
    print(parser.parse(prog))
