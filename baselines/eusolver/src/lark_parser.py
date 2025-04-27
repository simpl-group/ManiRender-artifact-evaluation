# -*- coding:utf-8 -*-

import re
from lark import Lark, Transformer

grammar = r"""
?prog : and_clause | or_clause | not_clause | predicate

and_clause : "(" "And"i prog prog ")"
or_clause : "(" "Or"i prog prog ")"
not_clause : "(" "Not"i prog ")"

predicate : pred1 | pred2
pred1 : "(" attr "x" ")"
pred2 : "(" attr "x" arg ")"

attr : /\w+/
arg : STRING | NUMBER

%import common.ESCAPED_STRING -> STRING
%import common.SIGNED_NUMBER -> NUMBER
%import common.WS
%ignore WS
"""


class Visitor(Transformer):
    def STRING(self, string):
        return str(string)[1:-2]

    def NUMBER(self, num):
        return eval(num)

    def attr(self, var):
        return str(var[0])

    def arg(self, arg):
        return arg[0]

    def pred1(self, pred):
        def _f(x: dict, **kwargs):
            attr, = pred
            return x.get(attr, False)

        return _f

    def pred2(self, pred):
        def _f(x: dict, **kwargs):
            attr, value = pred
            if kwargs.get("cls", None) == "Text":  # only text trigger dynamic functions
                if attr == "In":
                    return value in x.get('Context', '')
                elif attr == "StartsWith":
                    return str.startswith(x.get('Context', ''), value)
                elif attr == "EndsWith":
                    return str.endswith(x.get('Context', ''), value)
                elif attr == "Regex":
                    return re.search(value, x.get('Context', '')) is not None
                elif attr == "LengthLess":
                    return x.get('Length', 99999) < value
                elif attr == "LengthEq":
                    return x.get('Length', None) == value
                elif attr == "LengthGreater":
                    return x.get('Length', -99999) > value
                elif attr in x:
                    return x.get(attr, False)
                else:
                    raise NotImplementedError(attr)
            else:
                return x.get(attr, None) == value

        return _f

    def predicate(self, pred):
        return pred[0]

    def or_clause(self, clauses):
        def _f(x: dict, **kwargs):
            lhs, rhs = clauses
            return lhs(x, **kwargs) or rhs(x, **kwargs)

        return _f

    def and_clause(self, clauses):
        def _f(x: dict, **kwargs):
            lhs, rhs = clauses
            return lhs(x, **kwargs) and rhs(x, **kwargs)

        return _f

    def not_clause(self, clause):
        def _f(x: dict, **kwargs):
            return not clause[0](x, **kwargs)

        return _f


class Parser:
    def __init__(self):
        self.visitor = Visitor()
        self.parser = Lark(grammar, start="prog")

    def parse(self, program):
        return self.visitor.transform(self.parser.parse(program))


if __name__ == '__main__':
    prog = "(Or (AgeEq x 24) (LongCoat x))"
    parser = Parser()
    print(parser.parse(prog))
