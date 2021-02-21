#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
import tempfile


#
# Run command:
#
# tail -n <n> <filename>
#
# By default, this read the last 10 lines from <filename>.
#
def cmd_tail_n(filename, n=10, bufsize=8192):

    n = int(n)
    bufsize = int(bufsize)

    f = open(filename)
    f.seek(0,2)
    l = 1-f.read(1).count('\n')
    B = f.tell()
    while n >= l and B > 0:
            block = min(bufsize, B)
            B -= block
            f.seek(B, 0)
            l += f.read(block).count('\n')
    f.seek(B, 0)
    l = min(l,n)
    last_lines = f.readlines()[-l:]
    last_lines=''.join(last_lines)
    f.close()

    '''
    last_lines = ''
    with open(filename, 'r') as f:
        tmp = f.readlines()
        last_lines = ''.join(tmp)[-n:]
    '''
    
    return last_lines


if __name__ == '__main__':
    print(simple_argparse(cmd_tail_n, sys.argv[1:]))
