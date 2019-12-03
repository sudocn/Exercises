#!/usr/bin/python
import yaml
from pprint import pprint

def rectify(table):
    '''
    parse raw table (contains 'start', 'accepts' info) to pure transition table:
    1. start, accepts keys are removed
    2. make sure accepts is presented as list
    3. make sure each destination items are presentd as {src: {via:[dest,...]}} format
    '''
    start = str(table.pop('start'))
    accepts = map(str, table.pop('accepts'))
    for state in list(table.keys()):
        moves = table.pop(state) # moves should be a dict too
        
        # stringfy and listfy moves
        new_moves = {}
        for k,v in moves.items():
            if isinstance(v, list):
                new_moves[str(k)] = [ str(x) for x in v ]
            else:
                new_moves[str(k)] = [ str(v) ]

        # rebuild dict key
        table[str(state)] = new_moves

    return start, set(accepts)

def trans_table(y):
    #print yaml.dump(y)
    print('states:', [ x for x in y.keys() if x != 'start' and x != 'accepts'])
    print("-- y before rectify --")
    print(y)

    if isinstance(y['accepts'], str):   # in case there is one sole accept state
        y['accepts'] = [y['accepts']]
    start, accept =  rectify(y)
    print("-- y after rectify --")
    print(y)
    print("start", start, "accept", accept)

    return y, start, accept

def merge_subtable(parent, *sub):
    '''
    McNaughton-Yamada-Thompson algorithm
    merge contents (except 'start' and 'accepts') in sub tables to parent.
    
    This is safe because in M-Y-T algorithm, combinations always add new 
    transitions to exising states, seldomly changes original states. (with the
    only exception for concatenation, see cat_table()) 
    '''
    #print('sub = ',sub)
    for t in sub:
        for src,routes in t.items():
            if src == 'start' or src == 'accepts':
                continue
            if src in parent:
                parent_routes = parent[src]
                #assert(parent_routes, dict)
                for path, dest in parent_routes.items():
                    if path in routes:
                        routes[path].extend(dest)    # merge if both exist
                    else:
                        routes[path] = dest          # only in parent
                parent[src].update(routes)
            else:
                parent[src] = routes
    return parent

def cat_table(left, right):
    '''
    McNaughton-Yamada-Thompson algorithm
    b) r = st, concatenation
    '''
    newt = {'start':left['start'], 'accepts':right['accepts']}
    merge_subtable(newt, left)

    newright = right.copy()
    fr,to  = right['start'], left['accepts']    # rename right[start] to left[accepts] (merge)
    #
    # 2 possible places: outter key, inner items
    #
    # rename outter name
    if fr in newright:
        newright[to] = newright.pop(fr)    
    # rename inner names
    for k, v in newright.items(): # outter dict
        if k == 'start' or k == 'accepts':
            continue
        for ik, iv in v.items():     # loop inner dict keys
            if fr in iv:
                iv.remove(fr)
                iv.append(to)
    return merge_subtable(newt, newright)

def load_default(name):
    with open('tables.yaml') as f:
        ydict = yaml.load(f)

    '''
    for k,v  in ydict.items():
        print('== {} =='.format(k))
        print(v)
    '''
    return trans_table(ydict[name])

#
#
#
import unittest
class TCaseTableOp(unittest.TestCase):
    def test_load(self):
        t,s,a = load_default('t3_29')
        self.assertDictEqual(t, {1: {'a': [1, 2], 'b': 1}, 2: {'a': 2, 'b': [2, 3], 'E': 0}, '0': {'a': ['0', '1'], 'b': ['0']}})
        self.assertEqual(s, '0')
        self.assertSetEqual(a, {'3'})

    def test_merge(self):
        t1 = {'start': '1s', 'accepts': '2e', '1s': {'a':'1e'}}
        t2 = {'1e': {'b':'2e'}}
        t = merge_subtable(t1, t2)
        print(t)
        self.assertDictEqual(t, {'start': '1s', 'accepts': '2e', '1s': {'a': '1e'}, '1e': {'b': '2e'}})

    def test_cat(self):
        t1 = {'start': '1s', 'accepts': '1e', '1s': {'a':'1e'}}
        t2 = {'start': '2s', 'accepts': '2e', '2s': {'a':'2e'}}
        t = cat_table(t1, t2)
        print(t)
        self.assertDictEqual(t, {'start': '1s', 'accepts': '2e', '1s': {'a': '1e'}, '1e': {'a': '2e'}})

if __name__ == '__main__':
    y,start,accept = trans_table('t3_26')
    pprint(y)