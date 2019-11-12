#!/usr/bin/python
import yaml
from graphviz import Digraph
from transtable import trans_table

EMPTY = 'E'

def draw_graphviz(table, start, accept):
    '''
    Draw a NFA graph by transition table
    table: transition table
    start: start state
    accept: accepting states
    '''

    g = Digraph('NFA', filename='NFA.gv',
                graph_attr={'rankdir': 'LR', 'newrank':'true'},
                node_attr={'shape':'circle', 'fontname':'Source Code Pro'},
                edge_attr={'arrowhead':'normal', 'fontname':'Source Code Pro'})

    # create states
    #'''
    for state in sorted(table.keys()):
        if state in accept:
            g.node(state, shape='doublecircle')
        else:
            g.node(state)
    '''
    for s in accept:
        g.node(str(s), shape='doublecircle')
    '''

    # add start arrow
    g.node('start', shape='none')
    g.edge('start', start)

    # add tranistions
    #g.edges(['01', '12', '14', '23', '45', '36', '56', '67'])
    for src, trans in table.items():
        if trans is None: continue
        for symbol, dest_list in trans.items():
            for dest in dest_list:
                print "adding {} -{}-> {}".format(src, symbol, dest)
                '''
                g.edge(src, dest, symbol,
                       constraint = 'false' if symbol == 'E' else 'true'
                )
                '''
                label =  r'<&epsilon;>' if symbol == 'E' else symbol
                g.edge(src, dest, label)

    #g.edge('0', '7', 'E', constraint='false')
    #g.edge('6', '1', 'E', constraint='false')

    # draw 
    g.view()

def fa_alphabet(table):
    '''
    get valcabulary (all possible input, not including E) from a table
    '''
    v = []
    for s in table.values():
        v.extend(s.keys())

    res = set(v)
    return res - set(EMPTY)


trans = \
        '''
0:
    start:
    a: [0,1]
    b: 0
1:
    b: 2
2:
    b: 3
3:
    accept:
        '''


################################################################################
#
# NFA
#
################################################################################

class FA(object):
    def __init__(self, table, start, accept):
        self.table, self.start, self.accept = table, start, accept #trans_table(tab_name)
        self.alphabet = fa_alphabet(self.table)

    def draw(self):
        draw_graphviz(self.table, self.start, self.accept)

    def move(self, states, symbol):
        def move_one(table, state, symbol):
            #print "move_one", state, symbol
            return table[state].get(symbol, [])

        if isinstance(states, list):
            raise Exception("states must be set")
    
        if not isinstance(states, set):
            states = set( states )

        r = []
        [ r.extend(move_one(self.table, s, symbol)) for s in states ]
        #print r
        return set(r)            

    def Eclosure(self, states):

        if isinstance(states, list):
            raise Exception("states must be set")
    
        if not isinstance(states, set):
            states =  set( states )
    
        stack = list(states)
        ecl = states.copy()

        while stack:
            s = stack.pop()
            for t in self.move(s, EMPTY):
                if t not in ecl:
                    ecl.add(t)
                    stack.append(t)

        print 'e-closure: {} = {} '.format(sorted(states), sorted(ecl))
        return ecl

class NFA(FA):
    pass


'''
states: A, B, C
symbols: a, b

A:
  start:
  a: [A,B]
  b: A
B:
  a: B
  b: [C,D]
C:
  accept:
  a: C
'''

if __name__ == "__main__":
       fa_draw(trans)

       #draw(t3_26)
       #fa_draw(t3_30)
