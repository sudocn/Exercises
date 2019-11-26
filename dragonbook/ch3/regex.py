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
        assert(isinstance(node, Atom))
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
                    assert(isinstance(e, Atom))
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
    
    def transtable(self):
        return {'start':'unimplemented', 'accepts':'unimplemented'}

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
    
class Atom(Node):
    '''
    1. a single char
    2. a expression enclose by '()'
    '''
    def __init__(self, c):
        super(Atom, self).__init__()
        self.symbol = c

    def transtable(self):
        s,e = self.name+'s',self.name+'e'
        return {'start':s, 'accepts':e, s:{e:self.symbol}}

    def __str__(self):
        return self.symbol

class Closure(Node):
    op = '*'
    def __init__(self, node):
        super(Closure, self).__init__()
        self.children.append(node)

    def transtable(self):
        table = self.children[0].transtable().copy()
        os,oe = table['start'],table['accepts']
        s,e = self.name+'s',self.name+'e'
        merge_subtable(table, 
            {s:{os:'E', e:'E'}, 
            oe:{e:'E', os: 'E'}
            })
        table['start'] = s
        table['accepts'] = e
        return table

class Term(Node):
    '''
    All operation except Union '|'
    '''
    op = '+'
    def __init__(self, L, R):
        super(Term, self).__init__()

        self.children.append(L)
        self.children.append(R)

    def transtable(self):
        lt = self.children[0].transtable()
        rt = self.children[1].transtable()
        table = cat_table(lt, rt)
        print('Term: ', table)
        return table

class Expr(Node):
    '''
    '''
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
            'accepts':e, 
            s:{lt['start']:'E', rt['start']:'E'},
            lt['accepts']:{e:'E'},
            rt['accepts']:{e:'E'}
        }
        merge_subtable(table, lt, rt)
        return table
    
class Bracket(Node):
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

        table = root.transtable()
        print('toNFATable', table)
        return table


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
        for txt in arr:
            re = Regex(txt)
            t = re.getExpr()
            print('expr: {} -> {}'.format(txt, t))

class TCaseRegexConverter(unittest.TestCase):
    def test_toNFA(self):
        import nfa
        from transtable import trans_table
        conv = RegexConverter()
        #tree  = Regex.parse("a(b|c)*d|efg")#|c*")
        #tree  = Regex.parse("(a|b)*abb")#|c*")
        tree  = Regex.parse("(a|b)*abb(a|b)*")#|c*")
        table = conv.toNFATable(tree)
        t, s, e = trans_table(table)
        print("start",s)
        print("accepts",e)
        nfa.draw_graphviz(table, s, e)

    def test_toDFA(self):
        from nfa import NFA
        from dfa import DFA
        from transtable import trans_table
        conv = RegexConverter()
        #restr = "(a|b)*abb"
        restr = "(a|b)*abb(a|b)*"
        #restr = "((E|a)b*)*"
        tree  = Regex.parse(restr)
        table = conv.toNFATable(tree)
        nfa = NFA(*trans_table(table))
        nfa.draw()
        dfa = DFA.from_nfa(nfa)
        dfa.draw()

if __name__ == '__main__':
    import sys
    re = '(a|b)*abb#' if len(sys.argv) == 1 else sys.argv[1]
    expr = Regex.parse(re)
    print('cst:{}'.format(expr))
    expr.toAST()
    print('ast:{}'.format(expr))
    draw_graphviz(expr)

