#!/usr/bin/python
import yaml
from graphviz import Digraph 

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

def fa_parse(table):
    '''
    parse raw table (contains 'start', 'accept' info) to pure transition table .
    '''
    start = None
    accept = []

    for state in table.keys():
        moves = table.pop(state) # moves should be a dict too
        
        # handle start/accept special keys
        if 'start' in moves:
            start = str(state)
            moves.pop('start')
            
        if 'accept' in moves:
            accept.append(str(state))
            moves.pop('accept')

        # stringfy and listfy moves
        new_moves = {}
        for k,v in moves.items():
            if isinstance(v, list):
                new_moves[str(k)] = [ str(x) for x in v ]
            else:
                new_moves[str(k)] = [ str(v) ]

        # rebuild dict key
        table[str(state)] = new_moves

    return start, set(accept)

def fa_volcabulary(table):
    '''
    get valcabulary (all possible input, not including E) from a table
    '''
    v = []
    for s in table.values():
        v.extend(s.keys())

    res = set(v)
    return res - set(EMPTY)

def fa_table(yaml_or_dict):
    if isinstance(yaml_or_dict, str):
        y = yaml.load(yaml_or_dict)
    elif isinstance(yaml_or_dict, dict):
        y = yaml_or_dict
    else:
        raise Exception("fa_table only accepts yaml or dict")
    
    #print yaml.dump(y)
    print 'states:', y.keys()
    print "-- y before parse --"
    print y
    #draw(y, 0, [3])

    start, accept =  fa_parse(y)
    print "-- y after parse --"
    print y
    print "start", start, "accept", accept

    return y, start, accept

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
    def __init__(self, yaml_text):
        self.table, self.start, self.accept = fa_table(yaml_text)
        self.volcabulary = fa_volcabulary(self.table)

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

################################################################################
#
# DFA
#
################################################################################

class DState(object):
    '''
    Data structure for ONE DFA state
    '''
    def __init__(self, index, states=[], marked=False):
        self.index = index
        self.states = set(states)
        self.name = chr(ord('A') + self.index)
        self.marked = marked

    def __str__(self):
        return '{} {}'.format(self.name, sorted(self.states))

class DFA(FA):
    '''
    Definite finite automata

    after init, the DFA is not a full featured DFA, it is used a the input data structure for
    NFA2DFA. 

    User must call concolude() to make this class to acts normally
    '''
    
    def __init__(self):
        self.states = {}
        self.index = 0
        self.trans = {}

    def __str__(self):
        content = "======== DFA ========\n"
        content += "states\n"
        for k,v in self.states.items():
            content += '{} : {}\n'.format(k,v)

        content += "tansition\n"
        for src in sorted(self.trans.keys()):
            moves = self.trans[src]
            content += '{} : {}\n'.format(src, ', '.join([k + '->' + v for k,v in moves.items() ]))

        return content

    def mark(self, Tset):
        assert isinstance(Tset, set)
        for k,v in self.states.items():
            if v.states == Tset:
                v.marked = True
                return
        raise Exception("e-cloure set {} not found, can not mark it".format(T)) 

    def unmarked(self):
        for k,v in self.states.items():
            if not v.marked:
                return v.states
        return None

    def addState(self, Tset, start=False, accept=False):
        assert isinstance(Tset, set)
        if self.hasState(Tset):
            raise Exception("state {} already in states set".format(Tset))

        st = DState(self.index, Tset)
        self.states[self.index] = st

        self.trans[st.name] = {}
        if start:
            self.trans[st.name]["start"] = ''
        if accept:
            self.trans[st.name]["accept"] = ''

        print "  new State: {} {}".format(st.name, sorted(Tset))
        self.index += 1

    def _getState(self, Tset):
        assert isinstance(Tset, set)
        for k,v in self.states.items():
            if Tset == v.states:
                return v
        return None

    def hasState(self, Tset):
        assert isinstance(Tset, set)
        return self._getState(Tset) is not None

    def stateName(self, Tset):
        try:
            return self._getState(Tset).name
        except:
            return 'NONAME'
        
    def addEdge(self, sym, src, dst):
        src_name = self.stateName(src)
        dst_name = self.stateName(dst)
        print "  new Edge: {} {}-> {} ".format(src_name, sym, dst_name)

        if src_name not in self.trans:
            self.trans[src_name] = {}

        self.trans[src_name][sym] = dst_name

    def conclude(self):
        super(DFA, self).__init__(self.trans)
        
    #def draw(self):
    #    fa = FA(self.trans)
    #    fa.draw()
    def move(self, state, symbol):
        if isinstance(state, set):
            print state
            raise Exception("Error: DFA move only start from exactly 1 state")

        dest = super(DFA, self).move(state, symbol)
        if len(dest) != 1:
            raise Exception("Error: multi move path, not a DFA")
        return list(dest)[0]

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
