#!/usr/bin/python
import yaml
from pprint import pprint

def rectify(table):
    '''
    parse raw table (contains 'start', 'accepts' info) to pure transition table:
    1. start, accepts keys are removed
    2. make sure accepts is presented as list
    3. make sure each destination items are presentd as {src: {dest:[s,...]}} format
    '''
    start = str(table.pop('start'))
    accepts = map(str, table.pop('accepts'))
    for state in table.keys():
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
    print 'states:', [ x for x in y.keys() if x != 'start' and x != 'accepts']
    print "-- y before rectify --"
    print y

    if isinstance(y['accepts'], str):   # in case there is one sole accept state
        y['accepts'] = [y['accepts']]
    start, accept =  rectify(y)
    print "-- y after rectify --"
    print y
    print "start", start, "accept", accept

    return y, start, accept

def load_default(name):
    with open('tables.yaml') as f:
        ydict = yaml.load(f)

    '''
    for k,v  in ydict.items():
        print('== {} =='.format(k))
        print(v)
    '''
    return trans_table(ydict[name])

if __name__ == '__main__':
    y,start,accept = trans_table('t3_26')
    pprint(y)