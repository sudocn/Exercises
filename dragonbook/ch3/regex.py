#!/usr/bin/python
from graphviz import Digraph

class ParseError(Exception):
    pass

'''
Considering the most basic regular experssion, has 3 operations:

  Union: '|'
  Concatenation: '' (no symbol/empty symbol)
  (Kleene) closure: '*'

Besides, '()' are used to change priority.

The BNF for the regular expression are

  expr -> expr '|' term | term
  term -> term closure | closure
  closure -> atom* | atom
  atom -> char | (expr)

'''

global_index = 0
def unique_name(prefix):
    global global_index
    global_index += 1
    return prefix + str(global_index)
    

def draw_node(g, node):
    #s = node.name
    if node.isLeaf():
        # need labels otherwise we will have duplicate names
        g.node('a'+node.name, label=node.id)
        g.edge(node.name, 'a'+node.name)
    else:
        for e in node.children:
            draw_node(g, e)
            print("add edge {}->{}".format(node.name, e.name))
            g.edge(node.name, e.name)
    
def draw_graphviz(node):
    '''
    Draw a NFA graph by transition table
    table: transition table
    start: start state
    accept: accepting states
    '''

    g = Digraph('NFA', filename='parse_tree.gv',
                #graph_attr={'rankdir': 'LR', 'newrank':'true'},
                node_attr={'shape':'none', 'fontname':'Source Code Pro'},
                edge_attr={'arrowhead':'none', 'fontname':'Source Code Pro'})

    draw_node(g,node)

    g.view()

class Node(object):
    '''
    A RE node (regular expression node) base class
    '''
    global_index = 0
    type = 'NODE'
    def __init__(self, name=None):
        self._name = name
        self.children = []

    def isLeaf(self):
        return not self.children

    @property
    def name(self):
        if not self._name:
            self._name = unique_name('r') + (self.op if hasattr(self, 'op') else '')
        return self._name
        
    def __str__(self):
        '''
        res = '{}('.format(self.type)
        for child in self.children:
            res += '{},'.format(child)
        
        return res[:-1] + ')'
        '''
        return '{}({})'.format(self.op, ','.join(map(str, self.children)))

    @classmethod
    def reset(cls):
        cls.global_index = 0

    @classmethod
    def disabe_name(cls):
        name = 'r'+str(cls.global_index)
        cls.global_index += 1
        return name
    
class Atom(Node):
    '''
    1. a single char
    2. a expression enclose by '()'
    '''
    type = 'ATOM'
    def __init__(self, c):
        super(Atom, self).__init__()
        self.id = c

    def __str__(self):
        #return "{}({})".format(self.type, self.id)
        return self.id

class Closure(Node):
    type = 'CLOSURE'
    op = '*'
    def __init__(self, node):
        super(Closure, self).__init__()
        self.children.append(node)

    #def __str__(self):
    #    return "{}({}*)".format(self.type, self.children[0])

class Term(Node):
    '''
    All operation except Union '|'
    '''
    type = 'TERM'
    op = '+'
    def __init__(self, L, R):
        super(Term, self).__init__()

        self.children.append(L)
        self.children.append(R)

class Expr(Node):
    '''
    '''
    type = 'EXPR'
    op = '|'
    def __init__(self, L, R):
        super(Expr, self).__init__()

        self.children.append(L)
        self.children.append(R)
    
class Bracket(Node):
    type = 'PARA'
    op = '@'	# should be '()', use @ for readability
    def __init__(self, node):
        super(Bracket, self).__init__()
        self.children.append(node)
    
#
#
#

class RegexString(object):
    def __init__(self, re_str):
        self.text = re_str
        self.content = list(re_str)
    
    def getAtom(self):
        try:
            c = self.getc()
        except IndexError:
            return None

        if c == '(':
            # TODO: look ahead too far, new method needed
            lvl = 1
            for i,v in enumerate(self.content): # handle nested braces
                if v == '(':
                    lvl += 1
                elif v == ')':
                    lvl -= 1
                    if lvl == 0:
                        break
                
            end = self.content.index(')')
            txt = ''.join(self.content[:i])
            del self.content[:i+1]
            node = RegexString(txt).parse()
            #print 'para', ''.join(self.content)
            return Bracket(node)
        elif c in '*|)':
            self.putc(c)
            #return None
            raise ParseError('getAtom: {} is not an atom, remain str {}'.format(c, ''.join(self.content)))
        else:
            return Atom(c)

    def getClosure(self):
        atom = self.getAtom()
        if not atom: return None
        if self.peek() == '*':
            self.getc()
            return Closure(atom)
        else:
            return atom

    def getTerm(self):
        left = self.getClosure()
        if not left:    # ?? need ??
            return None
        while True:
            if self.peek() == '|':
                break
            right = self.getClosure()
            if not right:
                break
            left = Term(left, right)
            #right = self.getClosure()
        return left

    def getExpr(self):
        left = self.getTerm()
        if not left:    # ?? need ??
            return None
        while True:
            if self.peek() == '': # reach end
                break
            if self.peek() != '|':
                raise ParseError('getExpr: not a union, str {}'.format(''.join(self.content)))
            self.getc()
            right = self.getTerm()
            if not right:
                raise ParseError('getExpr: no term find after |, str {}'.format(''.join(self.content)))
            left = Expr(left, right)
        return left

    def parse(self):
        return self.getExpr()

    ############
    # utilities
    def peek(self):
        return self.content[0] if self.content else ''

    def getc(self):
        return self.content.pop(0)
    
    def putc(self, c):
        self.content[0:0] = c

class NodeStack(object):
    def __init__(self):
        self.stack = []

    def push(self, item):
        assert(isinstance(item, ReNode))
        self.stack.append(item)
        return item
    
    def pop(self):
        return self.stack.pop()

    def empty(self):
        return len(self.stack) == 0

    def __str__(self):
        return str(map(str, self.stack))

class ReTree(object):
    def __init__(self):
        self.stack = NodeStack()
        self.expr = None

    def _setRoot(self, root):
        assert(isinstance(root, ReNode))
        self.root = root

    def buildParenth(self):
        pass

    def buildOr(self):
        pass

    def getBlock(self):
        '''
        get a syntax block from re expression

        precedence:
        *
        ()
        cat
        |
        '''
        ch = self.expr.getchar()
        print "   ch -> {}".format(ch)

        if ch == '(':
            self.stack.push(ReNode.makeParenthNode())
        elif ch == ')':
            self.buildParenth()
        elif ch == '|':
            self.buildOr()
        elif ch == '*':
            pass
        else:
            current = ReNode.makeLeaf(ch)
            if self.stack.empty():
                self.stack.push(current)
            else:
                prev = self.stack.pop()
                cat = ReNode.makeCat(prev, current)
                self.stack.push(cat)

    def __str__(self):
        return self.stack.__str__()
    
    @classmethod
    def parse(cls, re_string):
        '''
        Main funtion to convert re string to parse tree
        '''
        tree = cls()

        re = RegexString(re_string)
        term = re.getTerm()
        
    
import unittest
class TCaseRegexString(unittest.TestCase):
    def test_getAtom(self):
        re = RegexString('abcdef')
        atom = re.getAtom()
        while atom:
            print(atom)
            atom = re.getAtom()

    def test_getClosure(self):
        re = RegexString('a*b*c*de*f*gh')
        cl = re.getClosure()
        while cl:
            print(cl)
            cl = re.getClosure()
    
    def test_getTerm(self):
        arr = [
            'a|*b*|c',
            'a*b*|c',
            'a*b*c'
        ]
        for txt in arr:
            re = RegexString(txt)
            t = re.getTerm()
            print('term: {} -> {}'.format(txt, t))

    def test_getExpr(self):
        arr = [
            'a|b',
            'a*|b*|c',
            'a*b*|c',
            'a*b*c',
            'abcdefghijk'
        ]
        for txt in arr:
            re = RegexString(txt)
            t = re.getExpr()
            print('expr: {} -> {}'.format(txt, t))

    def test_para(self):
        arr = [
            'a(b)',
            '(ab)*',
            '(ab)|b*|c',
            'a*(b*|c)*',
            'a*(b|c)*d',
            'abcdefghijk'
        ]
        for txt in arr:
            re = RegexString(txt)
            t = re.getExpr()
            print('expr: {} -> {}'.format(txt, t))

if __name__ == '__main__':
        print RegexString('(a*|b*)*').getClosure()
        #re = 'ab*cd|ef*g*hi*j|k'
        #re = '(a|b)*abb'
        #re = '(a*|b*)*'
        #re = '((E|a)b*)*'
        re = '(a|b)*abb(a|b)*'
        expr = RegexString(re).parse()

        draw_graphviz(expr)

