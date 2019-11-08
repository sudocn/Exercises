#!/usr/bin/python
#import yaml

from FA import NFA, DFA

t3_26 = \
'''
0: 
  start:
  E: [1,3]
1:
  a: 2
2:
  accept:
  a: 2
3:
  b: 4
4:
  accept:
  b: 4
'''

t3_29 = \
'''
0:
  start:
  a: [0,1]
  b: 0
1:
  a: [1,2]
  b: 1
2:
  a: 2
  b: [2,3]
  E: 0
3:
  accept:
'''

t3_30 =\
'''
0:
  start:
  E: 3
  a: 1
1:
  E: 0
  b: 2
2: 
  E: 1
  b: 3
3:
  accept:
  E: 2
  a: 0
'''

t3_21 = \
'''
0:
  start:
  E: [1,7]
1:
  E: [2,4]
2:
  a: 3
3:
  E: 6
4:
  b: 5
5:
  E: 6
6:
  E: [1, 7]
7:
  a: 8
8: 
  b: 9
9:
  b: 10
10:
  accept:
'''

def NFA2DFA(nfa):
    '''
    translate NFA to DFA, only use python set (DO NOT use DState)
    '''
    print
    print "== Start NFA to DFA converting =="
    print "volcabulary:", sorted(nfa.volcabulary)

    dfa = DFA()
    print "start:"
    S = nfa.Eclosure(nfa.start)
    dfa.addState(S, start=True,  accept=(len(nfa.accept & S) != 0))
    
    while dfa.unmarked():
        T = dfa.unmarked()
        dfa.mark(T)
        print "\nstate {} : {}".format(dfa.stateName(T), sorted(T))
        for sym in nfa.volcabulary:
            print sym + ":"
            M = nfa.move(T, sym)
            print "  move({}, {}) = {}".format(dfa.stateName(T), sym, sorted(M))
            U = nfa.Eclosure(M)
            #print "  e-closure({}) = {}".format(sorted(M), sorted(U))

            # remove dead states
            if not U:
                print "  dead state - remove"
                continue
            
            if not dfa.hasState(U):
                dfa.addState(U, accept=(len(nfa.accept & U) != 0))

            dfa.addEdge(sym, T, U)
        
    print dfa
    print dfa.trans
    dfa.conclude()
    return dfa

import unittest
from transtable import load_default
#fa_draw(NFA2DFA(NFA(t3_29)))
class testNFA2DFA(unittest.TestCase):
    def runTest(self):
        NFA2DFA(NFA(*load_default('t3_29'))).draw()

if __name__ == "__main__":
    unittest.main()
