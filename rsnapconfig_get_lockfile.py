#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
from configs.other_settings import DEFAULT_RSNAPSHOT_CONFIG_FILE


#/* Note: this is a temporary implementation and will be replaced in future version of pomeep */

#/* get lockfile from a rsnapconfig config file */
def rsnapconfig_get_lockfile():

    lockfile = ''

    with open(DEFAULT_RSNAPSHOT_CONFIG_FILE, 'r') as f:

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

                #/* is that line conatins lockfile only? */
                if len(tmp) >= 1:

                    #/* lockfile was found in the second splitterd value */
                    lockfile = tmp[1]

        #if not lockfile:
        #    raise Exception('no lockfile found in file {0}'.format(
        #        rsnapconfig_config_file))

    return os.path.realpath(lockfile)


if __name__ == '__main__':
    print(simple_argparse(rsnapconfig_get_lockfile, sys.argv[1:]))
