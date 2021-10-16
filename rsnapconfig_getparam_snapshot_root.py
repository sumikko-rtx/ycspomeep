#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
import re
from constants import DEFAULT_RSNAPSHOT_CONFIG_FILE


#/* Note: this is a temporary implementation and will be replaced in future version of ycspomeep */

#/* get parameter: snapshot_root from a rsnapconfig config file */
def rsnapconfig_getparam_snapshot_root(config_file=DEFAULT_RSNAPSHOT_CONFIG_FILE):

    result = ''

    with open(config_file, 'r') as f:

        #/* https://stackoverflow.com/questions/3277503/how-to-read-a-file-line-by-line-into-a-list */
        content_lines = f.readlines()

        #/* you may also want to remove whitespace characters like `\n` at the end of each line */
        content_lines = [x.strip() for x in content_lines]

        #/* look for snapshot_root */
        for x in content_lines:

            #/* skip empty line */
            if not x:
                continue

            #/* A hash mark (#) on the beginning of a line is treated as a comment. */
            if x[0] == '#':
                continue

            #/* ***important*** remove repeated TABs!!! */
            x = re.sub(r'\t+', '\t', x)

            #/* in rsnapconfig, parameters are split by TAB */
            tmp = x.split('\t')
            #print(tmp)

            #/* the first item x[0] must be exactly 'backup' */
            if not tmp[0].lower() == 'snapshot_root':
                continue

            #/* minimum # of parameters, including tmp[0]="backup": 2 */
            if len(tmp) < 2:
                continue

            #/* snapshot_root was found in the second splitterd value */
            result = tmp[1]

    result = os.path.realpath(result)

    return result


if __name__ == '__main__':
    print(simple_argparse(rsnapconfig_getparam_snapshot_root, sys.argv[1:]))
