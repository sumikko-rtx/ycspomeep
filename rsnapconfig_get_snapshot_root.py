#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
from configs.other_settings import DEFAULT_RSNAPSHOT_CONFIG_FILE


#/* Note: this is a temporary implementation and will be replaced in future version of pomeep */

#/* get snapshot_root from a rsnapconfig config file */
def rsnapconfig_get_snapshot_root():

    snapshot_root = ''

    with open(DEFAULT_RSNAPSHOT_CONFIG_FILE, 'r') as f:

        #/* https://stackoverflow.com/questions/3277503/how-to-read-a-file-line-by-line-into-a-list */
        content_lines = f.readlines()

        #/* you may also want to remove whitespace characters like `\n` at the end of each line */
        content_lines = [x.strip() for x in content_lines]

        #/* look for snapshot_root */
        for x in content_lines:

            if x.startswith('snapshot_root'):

                #/* rsnapconfig paremeters are split by TAB */
                tmp = x.split('\t')
                #print(tmp)

                #/* is that line conatins snapshot_root only? */
                if len(tmp) >= 1:

                    #/* snapshot_root was found in the second splitterd value */
                    snapshot_root = tmp[1]

        if not snapshot_root:
            raise Exception('no snapshot_root found in file {0}'.format(
                DEFAULT_RSNAPSHOT_CONFIG_FILE))

    return os.path.realpath(snapshot_root)


if __name__ == '__main__':
    print(simple_argparse(rsnapconfig_get_snapshot_root, sys.argv[1:]))
