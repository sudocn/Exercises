#!/usr/bin/python
#import yaml

from FA import NFA, DFA
from NFA2DFA import NFA2DFA
import unittest

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

def SimNFA(nfa, x):
    '''
    Algorithm 3.22: Simulating an NFA

    INPUT: An input string x terminated by an end-of-file character eof. An NFA
    N with start state s0, accepting states F, and transition function move.

    OUTPUT: Answer "yes" if M accepts x; "no" otherwise
    '''
    
    print
    print "== Start simulating NFA =="
    print "volcabulary:", sorted(nfa.volcabulary)

    xlist = list(x)
    
    S = nfa.Eclosure(nfa.start)
    print "start: {}".format(sorted(S))

    try:
        while True:
            print
            c = xlist.pop(0)
            m = nfa.move(S, c)
            S = nfa.Eclosure(m)
            print "char {}, move {}, S {}".format(c, sorted(m), sorted(S))
    except IndexError as e:
        print "finish simulate, S U F = {}".format(S & nfa.accept)
        if S & nfa.accept:
            print "yes"
            return True
        else:
            print "no"
            return False

def SimDFA(dfa, x):
    '''
    Algorithm 3.18: Simulating an DFA

    INPUT: An input string x terminated by an end-of-file character eof. An DFA
    D with start state s0, accepting states F, and transition function move.

    OUTPUT: Answer "yes" if D accepts x; "no" otherwise
    '''
    
    print
    print "== Start simulating DFA =="
    #print "volcabulary:", sorted(dfa.volcabulary)

    xlist = list(x)
    
    s = dfa.start
    print "start: {}".format(s),

    try:
        while True:
            c = xlist.pop(0)
            s = dfa.move(s, c)
            print " {}->  {}".format(c, s),
    except IndexError as e:
        print "finish simulate"
        if s in dfa.accept:
            print "yes"
            return True
        else:
            print "no"
            return False
        

#fa_draw(NFA2DFA(NFA(t3_29)))
class testSimNFA(unittest.TestCase):
    def runTest(self):
        #nfa = NFA(t3_29)
        nfa = NFA(t3_30)
        self.assertTrue(SimNFA(nfa, "aabb"))
        nfa.draw()

class testSimDFA(unittest.TestCase):
    def runTest(self):
        nfa = NFA(t3_30)
        dfa = NFA2DFA(nfa)
        dfa.draw()
        #print "dfa:", dfa.start, dfa.accept
        self.assertTrue(SimDFA(dfa, "aabb"))

if __name__ == "__main__":
    unittest.main()
