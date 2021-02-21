#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
import cmd_tail_n
import re
from rsnapconfig_get_retain_levels import rsnapconfig_get_retain_levels
from configs.other_settings import DEFAULT_RSNAPSHOT_INTERMEDIATE_ERROR_FILE


#/* check disk usage from snapshot_root, which defined in given rsnapshot config file
# * if there was an error while reading snapshot_root, this will return all zero values
# */
def rsnapshot_check_last_errors():

    #/* list of latestest rsnapshot error */
    rsnapshot_errors = []

    #/* get logfile from <snapshot_root>/alpha.0 */
    alpha_zero_dir = rsnapconfig_get_retain_levels(
        idx=0, include_snapshot_root=True)

    alpha_zero_dir = '{0}.0'.format(alpha_zero_dir)

    #/* list of possible log files */
    possible_log_files = [

        #/* from DEFAULT_RSNAPSHOT_INTERMEDIATE_ERROR_FILE  */
        DEFAULT_RSNAPSHOT_INTERMEDIATE_ERROR_FILE,

        #/* from rsnapshot_root/alpha.0 */
        os.path.realpath(
            os.path.join(alpha_zero_dir, 'rsnapshot.log')
        )
    ]

    #/************************************************************************/

    for j, x in enumerate(possible_log_files):

        try:

            with open(x, 'r') as f:

                #/* start at the last line of file */
                lines = f.readlines()
                j = len(lines) - 1

                while j > 0:

                    line = lines[j]
                    #line = line.lower()
                    line = line.strip()

                    #/* from rsnapreport.pl: colon must be follower by single space!!! */
                    if line.startswith('ERROR: ') or line.startswith('rsync error: '):
                        rsnapshot_errors.append(line)

                    #/* reach end of line??? */
                    if not line:
                        break

                    #/* prev line */
                    j = j - 1
                    
            #/* read success, exit immediately */
            break

        except Exception as e:
            if j > 0:
                print('WARNING: cannot read {0}: {1}'.format(x, e))

    return rsnapshot_errors


if __name__ == '__main__':
    print(simple_argparse(rsnapshot_check_last_errors, sys.argv[1:]))

