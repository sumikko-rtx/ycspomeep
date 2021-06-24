#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os


#
# Return the output from command: uname -a
#
def cmd_future_uname_a():

    tmp = []

    for x in os.uname():
        tmp.append(x)

    distribution_name = ' '.join(tmp)
    return distribution_name


if __name__ == '__main__':
    print(simple_argparse(cmd_future_uname_a, sys.argv[1:]))
