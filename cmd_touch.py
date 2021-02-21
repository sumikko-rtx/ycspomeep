#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
import datetime


#
# Run command:
# 
# touch <datetime> <input_filename1> <input_filename2> ...
#
# If datetime=None, assume datetime = datetime.datetime.now()
#
def cmd_touch(*filenames, datetime_=None):

    #/* https://stackoverflow.com/questions/1158076/implement-touch-using-python */

    if not datetime_:
        datetime_ = datetime.datetime.now()

    for x in filenames:

        #/* resolve link: output_file */
        x = os.path.realpath(x)

        #/* https://stackoverflow.com/questions/11348953/how-can-i-set-the-last-modified-time-of-a-file-from-python */
        try:

            #/* must convert into epoch time */
            epoch = datetime_.timestamp()
            os.utime(x, (epoch, epoch))

        except Exception as e:
            f = open(x, 'a+b')
            f.write(b'')
            f.close()


if __name__ == '__main__':
    print(simple_argparse(cmd_touch, sys.argv[1:]))
