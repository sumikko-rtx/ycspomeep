#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
from constants import DEFAULT_RSNAPSHOT_CONFIG_FILE


#/* Note: this is a temporary implementation and will be replaced in future version of ycspomeep */

#/* get parameter: lockfile from a rsnapconfig config file */
def rsnapconfig_getparam_lockfile(config_file=DEFAULT_RSNAPSHOT_CONFIG_FILE):

    result = ''

    with open(config_file, 'r') as f:

        #/* https://stackoverflow.com/questions/3277503/how-to-read-a-file-line-by-line-into-a-list */
        content_lines = f.readlines()

        #/* you may also want to remove whitespace characters like `\n` at the end of each line */
        content_lines = [x.strip() for x in content_lines]

        #/* look for lockfile */
        for x in content_lines:

            if x.startswith('lockfile'):

                #/* rsnapconfig paremeters are split by TAB */
                tmp = x.split('\t')
                #print(tmp)

                #/* minimum required paremeters num, including tmp[0]="lockfile": 2 */
                if len(tmp) >= 2:

                    #/* lockfile was found in the second splitterd value */
                    result = tmp[1]

    result = os.path.realpath(result)

    return result


if __name__ == '__main__':
    print(simple_argparse(rsnapconfig_getparam_lockfile, sys.argv[1:]))
