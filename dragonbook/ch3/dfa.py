#!/usr/bin/python
#import yaml

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

class DFA(FA):
    '''
    Definite finite automata
    '''

    @classmethod
    def from_nfa(cls, nfa):
        '''
        translate NFA to DFA, only use python set (DO NOT use DState)
        '''
        print
        print "== Start NFA to DFA converting =="
        print "volcabulary:", sorted(nfa.volcabulary)

        helper = DFAHelper()
        print "start:"
        S = nfa.Eclosure(nfa.start)
        helper.addState(S, start=True,  accept=(len(nfa.accept & S) != 0))
        
        while helper.unmarked():
            T = helper.unmarked()
            helper.mark(T)
            print "\nstate {} : {}".format(helper.stateName(T), sorted(T))
            for sym in nfa.volcabulary:
                print sym + ":"
                M = nfa.move(T, sym)
                print "  move({}, {}) = {}".format(helper.stateName(T), sym, sorted(M))
                U = nfa.Eclosure(M)
                #print "  e-closure({}) = {}".format(sorted(M), sorted(U))

                # remove dead states
                if not U:
                    print "  dead state - remove"
                    continue
                
                if not helper.hasState(U):
                    helper.addState(U, accept=(len(nfa.accept & U) != 0))

                helper.addEdge(sym, T, U)
            
        print helper
        print helper.trans

        return cls(*trans_table(helper.trans))


import unittest
from transtable import load_default
class testDFA(unittest.TestCase):
    def runTest(self):
        n = NFA(*load_default('t3_29'))
        d = DFA.from_nfa(n)
        d.draw()

if __name__ == "__main__":
    unittest.main()
