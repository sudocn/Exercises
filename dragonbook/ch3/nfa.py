#!/usr/bin/python
import yaml
from graphviz import Digraph
from transtable import trans_table, load_default

EMPTY = 'E'

def draw_graphviz(table, start, accepts):
    '''
    Draw a NFA graph by transition table
    table: transition table
    start: start state
    accepts: accepting states
    '''

    g = Digraph('NFA', filename='NFA.gv',
                graph_attr={'rankdir': 'LR', 'newrank':'true'},
                node_attr={'shape':'circle', 'fontname':'Source Code Pro'},
                edge_attr={'arrowhead':'normal', 'fontname':'Source Code Pro'})

    # create states
    for s in accepts:
        g.node(str(s), shape='doublecircle')

    # add start arrow
    g.node('start', shape='none')
    g.edge('start', start)

    # add tranistions
    #g.edges(['01', '12', '14', '23', '45', '36', '56', '67'])
    for src, trans in table.items():
        if trans is None: continue
        for dest, symbol_list in trans.items():
            for symbol in symbol_list:
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

################################################################################
#
# NFA
#
################################################################################

class FA(object):
    def __init__(self, table, start, accepts):
        self.table, self.start, self.accepts = table, start, accepts #trans_table(tab_name)

    @property
    def alphabet(self):
        '''
        get alphabet (all possible input, not including E) from a table
        '''
        v = []
        for s in self.table.values():
            for syms in s.values():
                v.extend(syms)

        res = set(v)
        return res - set(EMPTY)

    def draw(self):
        draw_graphviz(self.table, self.start, self.accepts)

    def move(self, states, symbol):
        def move_one(table, state, symbol):
            #print "move_one", state, symbol
            if state not in table:
                return []
            route = table[state]
            print("move_one:({},{}) {}".format(state, symbol, [k for k,v in route.items() if symbol in v]))
            return [k for k,v in route.items() if symbol in v]
            #return table[state].get(symbol, [])

        if isinstance(states, list):
            raise Exception("states must be set")
    
        if not isinstance(states, set):
            states = set( states )

        r = []
        [ r.extend(move_one(self.table, s, symbol)) for s in states ]
        #print r
        return set(r)            

    def Eclosure(self, states):
        '''
        e-closure operation, Figure 3.31 & 3.33
        '''
        if not isinstance(states, set):
            raise Exception("states must be set")
    
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


import unittest
class TCaseNfa(unittest.TestCase):
    def test_draw(self):
        t,s,a = load_default('t3_29')
        print('t:{}, s:{}, a:{}'.format(t,s,a))
        draw_graphviz(t,s,a)

if __name__ == "__main__":
       fa_draw(trans)

       #draw(t3_26)
       #fa_draw(t3_30)
