#!/usr/bin/env python
import yaml
from graphviz import Digraph
from transtable import trans_table, load_default

EMPTY = 'E'

def draw_graphviz(table, start, accepts, name='NFA'):
    '''
    Draw a NFA graph by transition table
    table: transition table
    start: start state
    accepts: accepting states
    '''

    g = Digraph('NFA', filename=name+'.gv',
                graph_attr={'rankdir': 'LR'},# 'newrank':'true'},
                node_attr={'shape':'circle', 'fontname':'Source Code Pro'},
                edge_attr={'arrowhead':'normal', 'fontname':'Source Code Pro'})

    assert(isinstance(start, str))
    print("\n== Draw graphviz ==")
    # add start arrow
    print("start node {}".format(start))
    g.node('start', shape='none')
    g.edge('start', start)

    # create states
    for s in accepts:
        print("accept node {}".format(s))
        g.node(str(s), shape='doublecircle')

    # add tranistions
    #g.edges(['01', '12', '14', '23', '45', '36', '56', '67'])
    for src, trans in table.items():
        if trans is None: continue
        for symbol, dest_list in trans.items():
            for dest in dest_list:
                print("edge {} -{}-> {}".format(src, symbol, dest))
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
    print("----  graphviz ----")
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
            v.extend(s.keys())

        res = set(v)
        return res - set(EMPTY)

    @property
    def allstates(self):
        S = set(self.table.keys())
        for ok in self.table.keys():
            for ik in self.table[ok].keys():
                S |= set(self.table[ok][ik])
        return S

    def draw(self):
        draw_graphviz(self.table, self.start, self.accepts, self.__class__.__name__)


    def move_one(self, state, symbol):
        #print "move_one", state, symbol
        if state not in self.table:
            return []
        print("    move_one:({},{}) {}".format(state, symbol, self.table[state].get(symbol,[])))
        return self.table[state].get(symbol, [])

    def move(self, states, symbol):

        if isinstance(states, list):
            raise Exception("states must be set")
    
        #if not isinstance(states, set):
        #    states = set( states )
        r = []
        [ r.extend(self.move_one(s, symbol)) for s in states ]
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
            for t in self.move_one(s, EMPTY):
                if t not in ecl:
                    ecl.add(t)
                    stack.append(t)

        print ('e-closure: {} = {} '.format(sorted(states), sorted(ecl)))
        return ecl

class NFA(FA):
    pass


import unittest
class TCaseNfa(unittest.TestCase):
    def test_draw(self):
        t,s,a = load_default('t3_29')
        print('t:{}, s:{}, a:{}'.format(t,s,a))
        try:
            draw_graphviz(t,s,a)
        except:
            pass

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        NFA(*load_default(sys.argv[1])).draw()
