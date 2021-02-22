#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
from constants import DEFAULT_RSNAPSHOT_CONFIG_FILE
from rsnapconfig_get_snapshot_root import rsnapconfig_get_snapshot_root

#/* Note: this is a temporary implementation and will be replaced in future version of ycspomeep */

#/* get all retain names from DEFAULT_RSNAPSHOT_CONFIG_FILE */


def rsnapconfig_get_retain_levels(idx=-1, include_snapshot_root=False):

    idx = int(idx)

    retain_levels = []

    #/************************************************************************/

    with open(DEFAULT_RSNAPSHOT_CONFIG_FILE, 'r') as f:

        #/* https://stackoverflow.com/questions/3277503/how-to-read-a-file-line-by-line-into-a-list */
        content_lines = f.readlines()

        #/* you may also want to remove whitespace characters like `\n` at the end of each line */
        content_lines = [x.strip() for x in content_lines]

        #/* look for snapshot_root */
        for x in content_lines:

            if x.startswith('retain'):

                #/* rsnapconfig paremeters are split by TAB */
                tmp = x.split('\t')
                # print(tmp)

                #/* is that line conatins snapshot_root only? */
                if len(tmp) >= 1:

                    #/* snapshot_root was found in the second splitterd value */
                    #/* append snapshot root if include_snapshot_root=True */
                    if include_snapshot_root:

                        snapshot_root = rsnapconfig_get_snapshot_root()

                        tmp[1] = os.path.realpath(
                            os.path.join(snapshot_root, tmp[1])
                        )

                    retain_levels.append(tmp[1])

        if not retain_levels:
            raise Exception('no snapshot_root found in file {0}'.format(
                DEFAULT_RSNAPSHOT_CONFIG_FILE))

    if idx < 0:
        return retain_levels
    else:
        idx = (idx % len(retain_levels))
        return retain_levels[idx]


if __name__ == '__main__':
    print(simple_argparse(rsnapconfig_get_retain_levels, sys.argv[1:]))
