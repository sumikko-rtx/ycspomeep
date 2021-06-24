#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import re
import os
from constants import DEFAULT_RSNAPSHOT_CRON_FILE
from cmd_rm import cmd_rm
from system_cmd import system_cmd
import tempfile




def cron_update_config(have_user_col=True, config_file=None):
    
    if not config_file:
        config_file = DEFAULT_RSNAPSHOT_CRON_FILE
    
    
    tmp_cron_file_content = []
    
    #/*---------------------------------------------------------------------*/
    
    with open(config_file,'r') as f:
        
        config_file_lines = f.read().splitlines()
        
        for line in config_file_lines:
            
            #/* remove comment after # */
            line = re.sub('#.*$', '', line)

            #/* skip empty line */
            line = line.strip()
            
            #print(line)
            if not line:
                continue

            #/* check if line begins with @ */
            have_at_xxx = bool(line.startswith('@'))

            #/* addition counts for have_user_col */
            n = 1 if have_user_col else 0

            #/* split entries */
            entries = line.split(None, (1 + n) if have_at_xxx else (5 + n))

            if have_at_xxx:

                #/* @reboot        Run once, at startup.
                # * @yearly        Run once a year, "0 0 1 1 *".
                # * @annually      (same as @yearly)
                # * @monthly       Run once a month, "0 0 1 * *".
                # * @weekly        Run once a week, "0 0 * * 0".
                # * @daily         Run once a day, "0 0 * * *".
                # * @midnight      (same as @daily)
                # * @hourly        Run once an hour, "0 * * * *".
                # */

                if entries[0] in ['@reboot']:

                    tmp_cron_file_content.append(
                        '{0} {1}'.format(
                            entries[0],
                            entries[1 + n],
                        )
                    )

                elif entries[0] in ['@yearly', '@annually']:

                    tmp_cron_file_content.append(
                        '{0} {1} {2} {3} {4} {5}'.format(
                            '0', '0', '1', '1', '*',
                            entries[1 + n],
                        )
                    )

                elif entries[0] in ['@monthly']:

                    tmp_cron_file_content.append(
                        '{0} {1} {2} {3} {4} {5}'.format(
                            '0', '0', '1', '*', '*',
                            entries[1 + n],
                        )
                    )

                elif entries[0] in ['@weekly']:

                    tmp_cron_file_content.append(
                        '{0} {1} {2} {3} {4} {5}'.format(
                            '0', '0', '*', '*', '0',
                            entries[1 + n],
                        )
                    )

                elif entries[0] in ['@daily', '@midnight']:

                    tmp_cron_file_content.append(
                        '{0} {1} {2} {3} {4} {5}'.format(
                            '0', '0', '*', '*', '*',
                            entries[1 + n],
                        )
                    )

                elif entries[0] in ['@hourly']:

                    tmp_cron_file_content.append(
                        '{0} {1} {2} {3} {4} {5}'.format(
                            '0', '*', '*', '*', '*',
                            entries[1 + n],
                        )
                    )
                    

                    
            else:
                tmp_cron_file_content.append(
                    '{0} {1} {2} {3} {4} {5}'.format(
                        entries[0],
                        entries[1],
                        entries[2],
                        entries[3],
                        entries[4],
                        entries[5 + n],
                    )
                )

    #/*---------------------------------------------------------------------*/

    #/* output tmp_cron_file_content to tmp_cron_file */
    handle, tmp_cron_file = tempfile.mkstemp()

    with os.fdopen(handle, 'w') as f:
        f.write('\n'.join(tmp_cron_file_content))

        #/* new crontab file must end with EOL*/
        f.write('\n')
    
    #/*---------------------------------------------------------------------*/
    
    #/* pass a tmp_cron_file_content to command: crontab <tmp_cron_file> */
    system_cmd(*['crontab', tmp_cron_file])
    
    #/*---------------------------------------------------------------------*/
    
    #/* remove tmp_cron_file_content */
    cmd_rm(tmp_cron_file, force=True)

    
    

if __name__ == '__main__':
    print(simple_argparse(cron_update_config, sys.argv[1:]))
