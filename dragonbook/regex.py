#!/usr/bin/python


class ReNode(object):
    '''
    A RE node (regular expression node) factory
    '''
    TYPE_NONE = 0
    TYPE_OR = 1
    TYPE_CAT = 2
    TYPE_CLOSURE = 3
    TYPE_PARENTH = 4
    TYPE_LEAF = 5

    global_index = 0

    def __init__(self, name, operator):
        self.name = name
        self.oper = operator
        self.left = None
        self.right = None

    def __str__(self):
        type_str = {0:'ERR', 1:'|', 2:'+', 3:'*', 4:'()', 5:''}
        if self.oper in (ReNode.TYPE_OR, ReNode.TYPE_CAT):
            return "{}{} [{} , {}]".format(self.name, type_str[self.oper],
                                                    self.left, self.right)
        else:
            return "<{}{}: {}>".format(self.name, type_str[self.oper], self.left)            

    @classmethod
    def reset(cls):
        cls.global_index = 0

    @classmethod
    def name(cls):
        name = 'r'+str(cls.global_index)
        cls.global_index += 1
        return name
    
    @classmethod
    def makeOr(cls, left, right):
        node = cls(cls.name(), ReNode.TYPE_OR)
        node.left = left
        node.right = right
        return node

    @classmethod
    def makeCat(cls, left, right):
        node = cls(cls.name(), ReNode.TYPE_CAT)
        node.left = left
        node.right = right
        return node
    
    @classmethod
    def makeClosure(cls, oprand):
        node = cls(cls.name(), ReNode.TYPE_CLOSURE)
        node.left = oprand
        return node

    @classmethod
    def makeParenth(cls, target):
        node = cls(cls.name(), ReNode.TYPE_PARENTH)
        node.left = target
        return node

    @classmethod
    def makeLeaf(cls, target):
        node = cls(cls.name(), ReNode.TYPE_LEAF)
        node.left = target
        return node

class Expression(object):
    def __init__(self, re_str):
        self.re_str = re_str
        self.expr = list(re_str)

    def peek(self):
        return self.expr[0]
    
    def getchar(self):
        return self.expr.pop(0)
    
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
        tree = cls()
        tree.expr = Expression(re_string)
        ReNode.reset()
        try:
            while True:
                tree.getBlock()
        except IndexError:
            print "Done."
            return tree
    
import unittest
class CaseReNode(unittest.TestCase):
    def testNodeCreate(self):
        n1 = ReNode.makeOr("LEFT", "RIGHT")
        print n1
        
        n2 = ReNode.makeCat("LEFT", "RIGHT")
        print n2

        n3 = ReNode.makeClosure("TARGET")
        print n3

        n4 = ReNode.makeParenth("TARGET")
        print n4

        n5 = ReNode.makeLeaf("LEAF")
        print n5

class CaseExpression(unittest.TestCase):
    def test_init(self):
        expr = Expression("abcdefg")
        self.assertEqual(expr.peek(), 'a')
        self.assertEqual(expr.getchar(), 'a')
        self.assertEqual(expr.getchar(), 'b')
        self.assertEqual(expr.peek(), 'c')
        self.assertEqual(expr.expr, list('cdefg'))

        #while True:
        #    expr.getchar()

class CaseReTree(unittest.TestCase):
    def testCat(self):
        tree = ReTree.parse("abcde")
        self.assertEqual(len( tree.stack.stack ) , 1)
        print tree.stack.stack[0]
        self.assertEqual(str(tree.stack.stack[0]),
                         'r8+ [r6+ [r4+ [r2+ [<r0: a> , <r1: b>] , <r3: c>] , <r5: d>] , <r7: e>]')
#        print tree
