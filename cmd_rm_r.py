#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
import shutil
from str_2_bool import str_2_bool
from system_cmd import system_cmd
import tempfile
import getopt


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

#             #/* fast rmtree method: rsync -a --delete empty_dir/ x/ */
#             empty_dir = tempfile.mkdtemp()
#             x = '{0}{1}'.format(x, os.sep)
#  
#             #print(['rsync', '-a', '--delete',
#             #         empty_dir, x])
#  
#             system_cmd(
#                 cmd=['rsync', '-a', '--delete',
#                      empty_dir, x],
#             )
#             shutil.rmtree(empty_dir)

            shutil.rmtree(x)



def cmd_rm_r(*filenames, force=False):

    force = str_2_bool(force)

    try:
        __cmd_rm_f(*filenames)

    except Exception as e:
        if not force:
            raise e


if __name__ == '__main__':
    
    #/* match the opengroup's rm specification */
    try:
        parsed_args, unparsed_args = getopt.getopt(sys.argv[1:], 'fiRr')
    except Exception as e:
        parsed_args, unparsed_args = [], sys.argv[1:]

    print(simple_argparse(cmd_rm_r, unparsed_args))
