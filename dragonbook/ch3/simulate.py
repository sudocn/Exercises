#!/usr/bin/python
#import yaml

from nfa import NFA
from dfa import DFA
from transtable import load_default

def SimNFA(nfa, x):
    '''
    Algorithm 3.22: Simulating an NFA

    INPUT: An input string x terminated by an end-of-file character eof. An NFA
    N with start state s0, accepting states F, and transition function move.

    OUTPUT: Answer "yes" if M accepts x; "no" otherwise
    '''
    
    print
    print "== Start simulating NFA =="
    print "alphabet:", sorted(nfa.alphabet)

    xlist = list(x)
    
    S = nfa.Eclosure(set([nfa.start]))
    print "start: {}".format(sorted(S))

    try:
        while True:
            print
            c = xlist.pop(0)
            m = nfa.move(S, c)
            S = nfa.Eclosure(m)
            print "char {}, move {}, S {}".format(c, sorted(m), sorted(S))
    except IndexError as e:
        print "finish simulate, S U F = {}".format(S & nfa.accepts)
        if S & nfa.accepts:
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
    print "alphabet:", sorted(dfa.alphabet)
    print "transtab:", dfa.table
    print "start:", dfa.start
    print "accepts:", dfa.accepts
    print "--------------------------"

    xlist = list(x)
    
    s = dfa.start
    print "start: {}".format(s),

    try:
        while True:
            c = xlist.pop(0)
            s = dfa.move(s, c)
            print " {}->  {}".format(c, s),
    except IndexError as e:
        print "finish simulate", 's=',s, 'accepts=', dfa.accepts
        if s in dfa.accepts:
            print "yes"
            return True
        else:
            print "no"
            return False
        
import unittest
class testSimNFA(unittest.TestCase):
    def runTest(self):
        #nfa = NFA(t3_29)
        nfa = NFA(*load_default('t3_30'))
        self.assertTrue(SimNFA(nfa, "aabb"))
        nfa.draw()

class testSimDFA(unittest.TestCase):
    def runTest(self):
        nfa = NFA(*load_default('t3_30'))
        dfa = DFA.from_nfa(nfa)
        dfa.draw()
        #print "dfa:", dfa.start, dfa.accepts
        self.assertTrue(SimDFA(dfa, "aabb"))

if __name__ == "__main__":
    unittest.main()
