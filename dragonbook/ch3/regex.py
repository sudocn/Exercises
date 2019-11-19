#!/usr/bin/python
from graphviz import Digraph

class ParseError(Exception):
    pass


def merge_subtable(parent, *sub):
    #print('sub = ',sub)
    for t in sub:
        for k,v in t.items():
            if k == 'start' or k == 'end':
                continue
            if k in parent:
                #parent[k] = parent[k].merge(v)
                parent[k].merge(v)
            else:
                parent[k] = v

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
    
    def transtable(self):
        return {'start':'unimplemented', 'end':'unimplemented'}

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

    def transtable(self):
        s,e = self.name+'s',self.name+'e'
        return {'start':s, 'end':e, s:{e:self.id}}

    def __str__(self):
        #return "{}({})".format(self.type, self.id)
        return self.id

class Closure(Node):
    type = 'CLOSURE'
    op = '*'
    def __init__(self, node):
        super(Closure, self).__init__()
        self.children.append(node)

    def transtable(self):
        table = self.children[0].transtable().copy()
        os,oe = table['start'],table['end']
        s,e = self.name+'s',self.name+'e'
        merge_subtable(table, 
            {s:{os:'E', e:'E'}, 
            oe:{e:'E', os: 'E'}
            })
        table['start'] = s
        table['end'] = e
        return table

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

    def transtable(self):
        lt = self.children[0].transtable()
        rt = self.children[1].transtable()
        s,e = self.name+'s',self.name+'e'
        table = {
            'start':lt['start'], 
            'end':rt['end'], 
        }
        merge_subtable(table, lt, rt)
        return table

class Expr(Node):
    '''
    '''
    type = 'EXPR'
    op = '|'
    def __init__(self, L, R):
        super(Expr, self).__init__()

        self.children.append(L)
        self.children.append(R)
    
    def transtable(self):
        lt = self.children[0].transtable()
        rt = self.children[1].transtable()
        s,e = self.name+'s',self.name+'e'
        table = {
            'start':s, 
            'end':e, 
            s:{lt['start']:'E', rt['start']:'E'},
            lt['end']:{e:'E'},
            rt['end']:{e:'E'}
        }
        merge_subtable(table, lt, rt)
        return table
    
class Bracket(Node):
    type = 'PARA'
    op = '@'	# should be '()', use @ for readability
    def __init__(self, node):
        super(Bracket, self).__init__()
        self.children.append(node)

    def transtable(self):
        return self.children[0].transtable()
    
#
#
#

class Regex(object):
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
            node = Regex.parse(txt)
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

    @classmethod
    def parse(cls, re_str):
        return cls(re_str).getExpr()

    ############
    # utilities
    def peek(self):
        return self.content[0] if self.content else ''

    def getc(self):
        return self.content.pop(0)
    
    def putc(self, c):
        self.content[0:0] = c


class RegexConverter(object):
    def traverse(self, node, func):
        for child in node.children:
            self.traverse(child, func)
        func(node)        

    def toNFATable(self, root):
        def proc(n):
            print("t:"+n.name, n.transtable())
        self.traverse(root, proc)



#
#
#
import unittest
class TCaseRegexString(unittest.TestCase):
    def test_getAtom(self):
        re = Regex('abcdef')
        atom = re.getAtom()
        while atom:
            print(atom)
            atom = re.getAtom()

    def test_getClosure(self):
        re = Regex('a*b*c*de*f*gh')
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
            re = Regex(txt)
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
            re = Regex(txt)
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
            re = Regex(txt)
            t = re.getExpr()
            print('expr: {} -> {}'.format(txt, t))

class TCaseRegexConverter(unittest.TestCase):
    def test_toNFA(sef):
        conv = RegexConverter()
        tree  = Regex.parse("abc|c*")
        conv.toNFATable(tree)

if __name__ == '__main__':
        print Regex('(a*|b*)*').getClosure()
        #re = 'ab*cd|ef*g*hi*j|k'
        #re = '(a|b)*abb'
        #re = '(a*|b*)*'
        #re = '((E|a)b*)*'
        re = '(a|b)*abb(a|b)*'
        expr = Regex.parse(re)

        draw_graphviz(expr)

