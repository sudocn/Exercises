#!/usr/bin/env python
#import yaml

from collections import defaultdict

from nfa import FA, NFA
from transtable import trans_table

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

class DFAHelper(object): 
    '''
    This class is not a full featured DFA, 
    it is used a the input data structure for coverting NFA to DFA. 
    '''   
    def __init__(self):
        self.states = {}
        self.index = 0
        self.trans = {'start':'', 'accepts':[]}

    def __str__(self):
        content = "======== DFA ========\n"
        content += "states\n"
        for k,v in self.states.items():
            content += '{} : {}\n'.format(k,v)

        content += "tansition\n"
        for src in sorted(self.trans.keys()):
            if src == 'accepts' or src == 'start':
                continue
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

    def addState(self, Tset, start=False, accepts=False):
        assert isinstance(Tset, set)
        if self.hasState(Tset):
            raise Exception("state {} already in states set".format(Tset))

        st = DState(self.index, Tset)
        self.states[self.index] = st

        self.trans[st.name] = {}
        if start:
            self.trans["start"] = st.name
        if accepts:
            self.trans["accepts"].append(st.name)

        print ("  new State: {} {}".format(st.name, sorted(Tset)))
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
        print ("  new Edge: {} {}-> {} ".format(src_name, sym, dst_name))

        if src_name not in self.trans:
            self.trans[src_name] = {}
        
        self.trans[src_name][sym] = dst_name
        
class DFA(FA):
    '''
    Definite finite automata
    '''

    def move(self, state, symbol):
        if isinstance(state, set):
            print (state)
            raise Exception("Error: DFA move only start from exactly 1 state")

        dest = super(DFA, self).move(state, symbol)
        if len(dest) != 1:
            raise Exception("Error: multi move path, not a DFA")
        return list(dest)[0]

    @classmethod
    def from_nfa(cls, nfa):
        '''
        translate NFA to DFA, only use python set (DO NOT use DState)
        '''
        print()
        print ("== Start NFA to DFA converting ==")
        print ("alphabet:", sorted(nfa.alphabet))

        helper = DFAHelper()
        print ("start:")
        S = nfa.Eclosure(set([nfa.start]))
        helper.addState(S, start=True,  accepts=(len(nfa.accepts & S) != 0))
        
        while helper.unmarked():
            T = helper.unmarked()
            helper.mark(T)
            print ("\nstate {} : {}".format(helper.stateName(T), sorted(T)))
            for sym in nfa.alphabet:
                print("  move({}, {}):".format(helper.stateName(T), sym))
                M = nfa.move(T, sym)
                print("  move({}, {}) = {}".format(helper.stateName(T), sym, sorted(M)))
                U = nfa.Eclosure(M)
                #print "  e-closure({}) = {}".format(sorted(M), sorted(U))

                # remove dead states
                if not U:
                    print ("  dead state - remove")
                    continue
                
                if not helper.hasState(U):
                    helper.addState(U, accepts=(len(nfa.accepts & U) != 0))

                helper.addEdge(sym, T, U)
            
        print(helper.trans)
        print(helper)

        dfa = cls(*trans_table(helper.trans))
        dfa.helper = helper
        return dfa

    #@classmethod
    def minimize(self):
        '''
        algorithm 3.39
        Minimize DFA states
        '''
        def part_index(state, parts):
            maps = [ 1 if state in x else 0 for x in parts]
            return maps.index(1)

        def mtag(state, II):
            '''
            Generate a text string tag for partition: the tag contains multplue pairs of 'sym:index' tuplue
            seprated by comma ','.  sym = symbol in alpabet, index = then value of move(state, sym)'s position
            in group II. 
            eg: 'a:A,b:B,c:B'
            '''
            tag = ''
            for sym in sorted(list(self.alphabet)):
                dest = self.move(state, sym)
                index = part_index(dest, II)
                #print('{}:{}({})'.format(sym,index,dest))
                tag += '{}:{},'.format(sym,index)
            return tag[:-1]
            
        def partition(II):
            IInew = []
            for G in II:
                if len(G) == 1:
                    print('  partition: + {}'.format(G))
                    IInew.append(G)
                    continue

                distribution = {s:mtag(s,II) for s in G}
                print(distribution)
                while distribution:
                    keys = list(distribution.keys())
                    car,cdr = keys[0],keys[1:]
                    group = set()
                    group.add(car)
                    for k in cdr:
                        if distribution[k] == distribution[car]:
                            group.add(k)
                            distribution.pop(k)
                    distribution.pop(car)
                    print('  partition: + {}'.format(group))
                    IInew.append(group)
            return IInew

        def part_equal(l1, l2):
            if len(l1) != len(l2):
                return False
            for e in l1:
                if e not in l2:
                    return False
            return True


        # initial partition
        # S - all states
        # F - accepting states
        # D - nonaccepting states

        # 1.
        S = self.allstates
        F = set(self.accepts)
        D = S - F
        II = [F, D]
        print('F={}, D={}, P={}'.format(F, D, II))

        # 2.
        IInew = partition(II)
        print("IInew = ", IInew)

        # 3
        while not part_equal(II, IInew):
            II = IInew
            IInew = partition(II)
            print("IInew = ", IInew)

        IIfin = IInew
        # 4.a
        Dn = [sorted(list(x))[0] for x in IIfin]    # D': the new states
        print(Dn)
        id_start = part_index(self.start, IIfin)
        new_start = Dn[id_start]

        # 4.b
        new_accepts = set()
        for ac in self.accepts:
            new_accepts.add(Dn[part_index(ac, IIfin)])

        print('new_start: {}, new_accepts: {}'.format(new_start, new_accepts))

        # 4.c
        new_table = defaultdict(dict)
        for src in Dn:
            for sym in self.alphabet:
                id_dest = part_index(self.move(src, sym), IIfin)
                new_table[src][sym] = [Dn[id_dest]]
        print('new_table: {}'.format(new_table))

        min_dfa = DFA(dict(new_table), new_start, new_accepts)
        print("== Minimized DFA ==")
        print(min_dfa)
        return min_dfa

import unittest
from transtable import load_default
class testDFA(unittest.TestCase):
    def runTest(self):
        n = NFA(*load_default('t3_30'))
        d = DFA.from_nfa(n)
        print("table:", d.table)
        self.assertDictEqual(d.table, {'A': {'a': ['A'], 'b': ['A']}})
        try:
            d.draw()
        except:
            pass

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:   # t3_21
        nfa = NFA(*load_default(sys.argv[1]))
        dfa = DFA.from_nfa(nfa)
        mdfa = dfa.minimize()
        mdfa.draw()
        print(mdfa.table)
        #dfa.draw()

