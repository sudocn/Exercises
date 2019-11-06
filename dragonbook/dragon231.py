#/usr/bin/python
import sys

class Node(object):
    name = 'NODE'
    def __init__(self):
        self.left = None
        self.right = None

class Expr(object):
    name = 'EXPR'
    pass

class Term(object):
    name = 'TERM'
    pass

def prefix_syntax_directed(code):


if __name__ == "__main__":
    code = '9-5+2'
    prefix_syntax_directed(code)
