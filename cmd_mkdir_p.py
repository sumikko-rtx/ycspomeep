#!/usr/bin/env python3
import sys
import os
from simple_argparse import simple_argparse
from cmd_mkdir import cmd_mkdir


#/* run command: mkdir -m  <mode> -p <dir1> <dir2>... 
# *
# * This code is for backward compatibility to the past ycspomeep codes.
# */
def cmd_mkdir_p(*dirs, mode=0o777):
    
    #/* TODO sumikko: AAA */
    if not isinstance(mode, int):
        mode = int(mode, 8)
        
    #/*---------------------------------------------------------------------*/
    
    cmd_mkdir(*dirs, mode=mode, parents=True)








if __name__ == '__main__':
    print(simple_argparse(cmd_mkdir_p, sys.argv[1:]))
