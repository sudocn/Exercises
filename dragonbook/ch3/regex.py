#!/usr/bin/python

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

class Node(object):
    '''
    A RE node (regular expression node) base class
    '''
    type = 'NODE'
    def __init__(self, name=None):
        self.name = name
        self.children = []

    def isLeaf(self):
        return not self.children

    def __str__(self):
        res = '{}('.format(self.type)
        for child in self.children:
            res += '{},'.format(child)
        
        return res[:-1] + ')'

    @classmethod
    def reset(cls):
        cls.global_index = 0

    @classmethod
    def name(cls):
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
        return "{}({})".format(self.type, self.id)

class Closure(Node):
    type = 'CLOSURE'
    def __init__(self, node):
        super(Closure, self).__init__()
        self.children.append(node)

    def __str__(self):
        return "{}({}*)".format(self.type, self.children[0])

class Term(Node):
    '''
    All operation except Union '|'
    '''
    type = 'TERM'
    def __init__(self, L, R):
        super(Term, self).__init__()

        self.children.append(L)
        self.children.append(R)

class Expr(Node):
    '''
    '''
    type = 'EXPR'
    def __init__(self, L, R):
        super(Expr, self).__init__()

        self.children.append(L)
        self.children.append(R)
    

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
            end = self.content.index(')')
            t = ''.join(self.content[:end])
            return Atom(t)
        elif c in '*|':
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
        if not left:
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
        re = RegexString('a|*b*|c')
        t = re.getTerm()
        print(t)

        re = RegexString('a*b*|c')
        t = re.getTerm()
        print(t)
        re = RegexString('a*b*c')
        t = re.getTerm()
        print(t)
        #    t = re.getTerm()

'''
class TCaseExpression(unittest.TestCase):
    def test_init(self):
        expr = RegexString("abcdefg")
        self.assertEqual(expr.peek(), 'a')
        self.assertEqual(expr.getchar(), 'a')
        self.assertEqual(expr.getchar(), 'b')
        self.assertEqual(expr.peek(), 'c')
        self.assertEqual(expr.expr, list('cdefg'))

        #while True:
        #    expr.getchar()

class TCaseReTree(unittest.TestCase):
    def testCat(self):
        tree = ReTree.parse("abcde")
        self.assertEqual(len( tree.stack.stack ) , 1)
        print tree.stack.stack[0]
        self.assertEqual(str(tree.stack.stack[0]),
                         'r8+ [r6+ [r4+ [r2+ [<r0: a> , <r1: b>] , <r3: c>] , <r5: d>] , <r7: e>]')
#        print tree
'''