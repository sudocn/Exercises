#!/usr/bin/python
from graphviz import Digraph
from transtable import cat_table, merge_subtable

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
        assert(isinstance(node, AtomNode))
        if node.ast:
            return  # Leaf node has nothing to do in AST
        # need labels otherwise we will have duplicate names
        g.node('a'+node.name, label=node.symbol)
        g.edge(node.name, 'a'+node.name)
    else:
        frm = node.name
        for e in node.children:
            assert(e.ast == node.ast)    # chilren inherit parent's ast attribut
            draw_node(g, e)

            to = e.name
            if e.ast:
                if e.isLeaf():
                    assert(isinstance(e, AtomNode))
                    label = e.symbol
                else:
                    label = e.op
                g.node(e.name, label)

            print("add edge {}->{}".format(frm, to))
            g.edge(frm, to)
    
def draw_graphviz(root):
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

    if root.ast:
        g.node(root.name, root.op)
    draw_node(g,root)

    g.view()

class Node(object):
    '''
    A RE node (regular expression node) base class
    '''
    global_index = 0
    def __init__(self, name=None):
        self._name = name
        self.ast = False    # this node is in an AST (if Ture) or CST (False, default)
        self.children = []
        self._followpos = set()

    def isLeaf(self):
        return not self.children
    
    def toAST(self):
        '''
        transform CST tree to AST
        '''
        self.ast = True
        if not self.isLeaf():
            for i,c in enumerate(self.children):
                if isinstance(c, Bracket):
                    self.children[i] = c.children[0]
            for c in self.children:
                c.toAST()
        return self
    
    def transtable(self):
        return {'start':'unimplemented', 'accepts':'unimplemented'}

    def traverse(self, func):
        for child in self.children:
            child.traverse(func)
        func(self)

    @property
    def left(self):
        return self.children[0]
    
    @property
    def right(self):
        return self.children[1]

    @property
    def name(self):
        if not self._name:
            self._name = unique_name('r') + (self.op if hasattr(self, 'op') else '')
        return self._name
        
    def __str__(self):
        return '{}({})'.format(self.op, ','.join(map(str, self.children)))

    @classmethod
    def reset(cls):
        cls.global_index = 0

    @classmethod
    def disabe_name(cls):
        name = 'r'+str(cls.global_index)
        cls.global_index += 1
        return name
    
class AtomNode(Node):
    '''
    1. a single char
    2. a expression enclose by '()'
    '''
    def __init__(self, c):
        super(AtomNode, self).__init__()
        self.symbol = c
        self.id = 0     # position in AST

    def transtable(self):
        s,e = self.name+'s',self.name+'e'
        return {'start':s, 'accepts':e, s:{e:self.symbol}}

    def nulllable(self):
        return False if self.symbol != 'E' else True
    
    def firstpos(self):
        return set() if self.nulllable() else set((self.id,))

    def lastpos(self):
        return self.firstpos()

    def followpos(self):
        pass

    def __str__(self):
        return self.symbol

class StarNode(Node):
    '''
    Closure
    closure -> atom* | atom
    '''
    op = '*'
    def __init__(self, node):
        super(StarNode, self).__init__()
        self.children.append(node)

    def transtable(self):
        table = self.left.transtable().copy()
        os,oe = table['start'],table['accepts']
        s,e = self.name+'s',self.name+'e'
        merge_subtable(table, 
            {s:{os:'E', e:'E'}, 
            oe:{e:'E', os: 'E'}
            })
        table['start'] = s
        table['accepts'] = e
        return table

    @property
    def right(self):
        raise Exception("Start Node has no right child")

    def nulllable(self):
        return True
    
    def firstpos(self):
        return self.left.firstpos()

    def lastpos(self):
        return self.left.lastpos()

    def followpos(self):
        pass

class CatNode(Node):
    '''
    cat
    term -> term closure | closure
    All operation except Union '|'
    '''
    op = '+'
    def __init__(self, L, R):
        super(CatNode, self).__init__()

        self.children.append(L)
        self.children.append(R)

    def transtable(self):
        lt = self.left.transtable()
        rt = self.right.transtable()
        table = cat_table(lt, rt)
        print('Term: ', table)
        return table

    def nulllable(self):
        return self.left.nulllable() and self.right.nulllable()

    def firstpos(self):
        if self.left.nulllable():
            return self.left.firstpos() | self.right.firstpos()
        else:
            return self.left.firstpos()    

    def lastpos(self):
        if self.right.nulllable():
            return self.left.lastpos() | self.right.lastpos()
        else:
            return self.right.lastpos()    

    def followpos(self):
        pass

class OrNode(Node):
    '''
    or
    expr -> expr '|' term | term 
    '''
    op = '|'
    def __init__(self, L, R):
        super(OrNode, self).__init__()

        self.children.append(L)
        self.children.append(R)
    
    def transtable(self):
        lt = self.left.transtable()
        rt = self.right.transtable()
        s,e = self.name+'s',self.name+'e'
        table = {
            'start':s, 
            'accepts':e, 
            s:{lt['start']:'E', rt['start']:'E'},
            lt['accepts']:{e:'E'},
            rt['accepts']:{e:'E'}
        }
        merge_subtable(table, lt, rt)
        return table

    def nulllable(self):
        return self.left.nulllable() or self.right.nulllable()
    
    def firstpos(self):
        return self.left.firstpos() | self.right.firstpos()

    def lastpos(self):
        return self.left.lastpos() | self.right.lastpos()

    def followpos(self):
        pass

class Bracket(Node):
    '''
    Only CST has this type of node, AST does not
    '''
    op = '@'	# should be '()', use @ for readability
    def __init__(self, node):
        super(Bracket, self).__init__()
        self.children.append(node)

    def transtable(self):
        return self.left.transtable()

    @property
    def right(self):
        raise Exception("Bracket Node has no right child")
    
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
            node = Regex(txt).getExpr()
            #print 'para', ''.join(self.content)
            return Bracket(node)
        elif c in '*|)':
            self.putc(c)
            #return None
            raise ParseError('getAtom: {} is not an atom, remain str {}'.format(c, ''.join(self.content)))
        else:
            return AtomNode(c)

    def getClosure(self):
        atom = self.getAtom()
        if not atom: return None
        if self.peek() == '*':
            self.getc()
            return StarNode(atom)
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
            left = CatNode(left, right)
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
            left = OrNode(left, right)
        return left

    @classmethod
    def parse(cls, re_str, ast=True):
        root = cls(re_str).getExpr()
        if ast:
            root.toAST()
        return root

    ############
    # utilities
    def peek(self):
        return self.content[0] if self.content else ''

    def getc(self):
        return self.content.pop(0)
    
    def putc(self, c):
        self.content[0:0] = c


class RegexConverter(object):
    @staticmethod
    def toNFATable(root):
        def proc(n):
            print("t:"+n.name, n.transtable())
        root.traverse(proc)

        table = root.transtable()
        print('toNFATable', table)
        return table

    @staticmethod
    def toDFA_prepare(root):
        impt_states = []
        def addleaf(x):
            if x.isLeaf():
                impt_states.append(x)

        def followpos(s):
            if isinstance(s, CatNode):
                left_last = s.left.lastpos()
                right_first = s.right.firstpos()
                for i in left_last:
                    impt_states[i]._followpos |= right_first
            elif isinstance(s, StarNode):
                last = s.lastpos()
                first = s.firstpos()
                for i in last:
                    impt_states[i]._followpos |= first
            
        root.traverse(addleaf)
        for i,v in enumerate(impt_states):  # numbering
            v.id = i
        
        root.traverse(followpos)
        for x in impt_states:
            print(" {}: {} {} {} / {}".format(
                x.id,   
                x.symbol, 
                [m for m in x.firstpos()], 
                [m for m in x.lastpos()], 
                [m for m in x._followpos]))

    @staticmethod
    def toDFA(re_str):
        ast = Regex.parse(re_str+'#').toAST()
        RegexConverter.toDFA_prepare(root)
        Dstates = [root.firstpos()]
        

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

        arr_cst = [
            ('a|b',     '|(a,b)'),
            ('a*|b*|c', '|(|(*(a),*(b)),c)'),
            ('a*b*|c',  '|(+(*(a),*(b)),c)'),
            ('a*b*c',   '+(+(*(a),*(b)),c)'),
            ('abcdefghijk','+(+(+(+(+(+(+(+(+(+(a,b),c),d),e),f),g),h),i),j),k)')
        ]
        for txt,result in arr_cst:
            re = Regex(txt)
            t = re.getExpr()
            print('expr: {} -> {}'.format(txt, t))
            self.assertEqual(str(t),result)

    def test_bracket(self):
        arr = [
            ('a(b)',        '+(a,@(b))'),
            ('(ab)*',       '*(@(+(a,b)))'),
            ('(ab)|b*|c',   '|(|(@(+(a,b)),*(b)),c)'),
            ('a*(b*|c)*',   '+(*(a),*(@(|(*(b),c))))'),
            ('a*(b|c)*d',   '+(+(*(a),*(@(|(b,c)))),d)'),
            ('(a)b(c(d(e(f)(g)h)i))(j)k', '+(+(+(+(@(a),b),@(+(c,@(+(+(d,@(+(+(+(e,@(f)),@(g)),h))),i))))),@(j)),k)')
        ]
        for txt,result in arr:
            re = Regex(txt)
            t = re.getExpr()
            print('expr: {} -> {}'.format(txt, t))
            self.assertEqual(str(t), result)

class TCaseRegexConverter(unittest.TestCase):
    def test_toNFA(self):
        import nfa
        from transtable import trans_table
        #tree  = Regex.parse("a(b|c)*d|efg")#|c*")
        tree  = Regex.parse("(a|b)*abb#", False)#|c*")
        #tree  = Regex.parse("(a|b)*abb(a|b)*")#|c*")
        table = RegexConverter.toNFATable(tree)
        t, s, e = trans_table(table)
        print("start",s)
        print("accepts",e)
        nfa.draw_graphviz(table, s, e)

    def test_toDFA(self):
        from nfa import NFA
        from dfa import DFA
        from transtable import trans_table
        #restr = "(a|b)*abb"
        restr = "(a|b)*abb(a|b)*"
        #restr = "((E|a)b*)*"
        tree  = Regex.parse(restr, False)
        table = RegexConverter.toNFATable(tree)
        nfa = NFA(*trans_table(table))
        nfa.draw()
        dfa = DFA.from_nfa(nfa)
        dfa.draw()

class TCaseDFA(unittest.TestCase):
    def test_firstpos(self):
        expr = Regex.parse("(a|b)*abb#")
        print(expr.firstpos())

if __name__ == '__main__':
    import sys
    re = '(a|b)*abb#' if len(sys.argv) == 1 else sys.argv[1]
    expr = Regex.parse(re)
    print('ast:{}'.format(expr))
    draw_graphviz(expr)

    RegexConverter.toDFA(expr)
    def printnode(x):
        print("  {} {} {} / {}".format(
            x.name, 
            [m for m in x.firstpos()], 
            [m for m in x.lastpos()], 
            [m for m in x._followpos]))
    #expr.traverse(printnode)

