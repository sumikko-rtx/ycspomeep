#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
import shutil
from str_2_bool import str_2_bool


#
# Run command:
#
# rm -r <input_filename1> <input_filename2> ...
#
# if force=True, add -f into the above command
#
def __cmd_rm_f(*filenames):

    #/* https://stackoverflow.com/questions/814167/easiest-way-to-rm-rf-in-python */
    for x in filenames:

        #/* resolve link: x */
        x = os.path.realpath(x)

        #/* os.remove(x) failed if try to delete non-empty dir */
        try:
            os.remove(x)

        except Exception as e:

            #if os.path.isdir(x) and not os.path.islink(x):
            shutil.rmtree(x)


def cmd_rm_r(*filenames, force=False):

    force = str_2_bool(force)

    try:
        __cmd_rm_f(*filenames)

    except Exception as e:
        if not force:
            raise e


if __name__ == '__main__':
    print(simple_argparse(cmd_rm_r, sys.argv[1:]))
