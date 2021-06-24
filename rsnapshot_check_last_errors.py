#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
from rsnapconfig_get_retain_levels import rsnapconfig_get_retain_levels
from constants import DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE, DEFAULT_RSNAPSHOT_INTERMEDIATE_ERROR_FILE


#/* check disk usage from snapshot_root, which defined in given rsnapshot config file
# * if there was an error while reading snapshot_root, this will return all zero values
# */
def rsnapshot_check_last_errors():

    #/* list of latestest rsnapshot error */
    rsnapshot_errors = []

    #/* the lastest logfile is saved to
    # *
    # *     <snapshot_root>/alpha.0
    # *     DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE
    # */
    
    #alpha_zero_dir = rsnapconfig_get_retain_levels(idx=0, include_snapshot_root=True)
    #alpha_zero_dir = '{0}.0'.format(alpha_zero_dir)

    #/* list of possible log files */
    possible_log_files = [

        DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE,
        DEFAULT_RSNAPSHOT_INTERMEDIATE_ERROR_FILE,

        #/* from rsnapshot_root/alpha.0 */
        #os.path.realpath(
        #    os.path.join(alpha_zero_dir, 'rsnapshot.log')
        #)
    ]

    #/************************************************************************/

    for j, x in enumerate(possible_log_files):
    
        print('INFO: reading {0}'.format(x))
        
        try:

            with open(x, 'r') as f:

                #/* start at the last line of file */
                lines = f.read().split('\n')
                j = len(lines) - 1

                while j >= 0:

                    line = lines[j]
                    #line = line.lower()
                    line = line.strip()
                    
                    #print(j,line)

                    #/* Find the line starts with "ERROR: " only!!!
                    # * (colon followed by single space)
                    # */
                    if line.startswith('ERROR: '):
                        rsnapshot_errors.append(line)

                    #/* prev line */
                    j = j - 1

        except Exception as e:
            #print(e)
            pass


    #/* remove duplicated rsnapshot_errors */
    rsnapshot_errors = list(set(rsnapshot_errors))

    return rsnapshot_errors


if __name__ == '__main__':
    print(simple_argparse(rsnapshot_check_last_errors, sys.argv[1:]))

