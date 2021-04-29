#!/usr/bin/env python3
import sys
import os
from simple_argparse import simple_argparse


def cmd_mkdir_p(*dirs):

    for x in dirs:

        try:
            os.makedirs(x)

        #/* skip if file exists!!! */
        except FileExistsError:
            pass


if __name__ == '__main__':
    print(simple_argparse(cmd_mkdir_p, sys.argv[1:]))
