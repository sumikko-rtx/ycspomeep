#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from cmd_rm import cmd_rm


#/* run command: rm -r <file> <file>...
# *
# * If force = True, replace parameter -r by -rf.
# * 
# * This code is for backward compatibility to the past ycspomeep codes.
# */
def cmd_rm_r(*files, force=False):
    cmd_rm(*files, recursive=True, force=force)



if __name__ == '__main__':
    print(simple_argparse(cmd_rm_r, sys.argv[1:]))
