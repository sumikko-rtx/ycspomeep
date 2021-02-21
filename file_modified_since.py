#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
import datetime


#
# return time duration (in seconds) since last modifed
# from given filename
#
def file_modified_since(filename):

    t2 = datetime.datetime.now()
    t1 = os.path.getctime(filename)
    t1 = datetime.datetime.fromtimestamp(t1)
    t_diff = t2 - t1

    return t_diff.total_seconds()


if __name__ == '__main__':
    print(simple_argparse(file_modified_since, sys.argv[1:]))
