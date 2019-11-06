#!/usr/bin/python

class Node(object):
    def __init__(self, sym, index, flwpos=None):
        self.symbol = sym
        self.index = index
        self.nullable = False
        self.firstpos = [index]
        self.lastpos = [index]
        self.followpos = flwpos

States = [
    Node('a', 1, [1,2,3]),
    Node('b', 2, [1,2,3]),
    Node('a', 3, [4]),
    Node('b', 4, [5]),
    Node('b', 5, [6]),
    Node('#', 6, []),
]

S_init = [1,2,3]
Dstats = [[S_init,0]]

def hasUnmarked():
    for s in Dstats:
        if s[1] == 0:
            return True
    return False

def getUnmarked():
    for s in Dstats:
        if s[1] == 0:
            return s
    return None

print(Dstats)
while hasUnmarked():
    s = getUnmarked()
    s[1] = 1
    print(Dstats)
