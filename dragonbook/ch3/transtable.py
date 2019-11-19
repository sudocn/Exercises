#!/usr/bin/python
import yaml
from pprint import pprint

def fa_parse(table):
    '''
    parse raw table (contains 'start', 'accepts' info) to pure transition table .
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
    print 'states:', y.keys()
    print "-- y before parse --"
    print y

    start, accept =  fa_parse(y)
    print "-- y after parse --"
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