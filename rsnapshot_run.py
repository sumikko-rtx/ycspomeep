#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
from system_cmd import system_cmd
from configs.other_settings import DEFAULT_RSNAPSHOT_CONFIG_FILE, PROGRAM_DIR,\
    DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE,\
    DEFAULT_RSNAPSHOT_INTERMEDIATE_ERROR_FILE
from rsnapconfig_get_snapshot_root import rsnapconfig_get_snapshot_root
from email_report import email_report
from cmd_rm_r import cmd_rm_r
from cmd_cat import cmd_cat

# this script does the following:
#
# rsnapshot rsnapshot.cfg alpha 2>&1 | tee snapshot_root/alpha.0/rsnapshot.log | rsnapreport.pl | email_report.update
# (1)                                  (2)                                       (3)              (4)
#
# (1) run rsnapshot backup
# (2) save all rsnapshot progress into log
# (3) use that file generate the backup summary
# (4) email that summary to recipients
#
# to properly run this script, you must set
#
# (1) verbose >= 4
# (2) add --stats to rsync_long_args
#
# in the rsnapshot.conf
#
# this script shall capture all rsnapshot errors
#including CTRL+C interrupt
#


def rsnapshot_run(config_file=DEFAULT_RSNAPSHOT_CONFIG_FILE, retain_level='alpha'):

    snapshot_root = rsnapconfig_get_snapshot_root()

    final_logfile = os.path.realpath(
        os.path.join(
            snapshot_root,
            '{0}.0'.format(retain_level),
            'rsnapshot.log',
        )
    )

    try:

        #/* (1) */

        cmd = ['rsnapshot', '-c', config_file, retain_level]
        print('INFO: running {0}'.format(cmd))

        return_code, output, error, elapsed_n_seconds = system_cmd(
            cmd=cmd,
            output_file=DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE,
            error_file=DEFAULT_RSNAPSHOT_INTERMEDIATE_ERROR_FILE,
            raise_exception=False,
        )

    #/* is CTRL+C is pressed? */
    except KeyboardInterrupt as e:
        pass
        #tmp = 'ERROR: rsnapshot was interrupted by user'
        #error = '{0}\n{1}'.format(error, tmp)

    finally:

        #print('--- begin of DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE ---')
        #print(cmd_cat(None, DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE))
        #print('--- end of DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE ---')

        #print('--- begin of DEFAULT_RSNAPSHOT_INTERMEDIATE_ERROR_FILE ---')
        #print(cmd_cat(None, DEFAULT_RSNAPSHOT_INTERMEDIATE_ERROR_FILE))
        #print('--- end of DEFAULT_RSNAPSHOT_INTERMEDIATE_ERROR_FILE ---')

        #/* (2) */
        #/* stream redirection: 2>&1, forming intermediate file, tmpfile */
        cmd_rm_r(final_logfile, force=True)
        cmd_cat(final_logfile,
                DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE,
                DEFAULT_RSNAPSHOT_INTERMEDIATE_ERROR_FILE,
                truncate=True)

        #/* (3) */
        #/* note: rsnapreport.pl must be placed in the pomeep root directory.*/
        print('INFO: generating rsnapshot summary...')

        rsnapreport_pl = os.path.realpath(
            os.path.join(
                PROGRAM_DIR,
                'rsnapreport.pl',
            )
        )

        return_code, output, error, elapsed_n_seconds = system_cmd(
            cmd=['perl',  rsnapreport_pl],
            input_file=final_logfile,
            raise_exception=False,
        )

        #/* output is a rsnapshot summary */
        print('')
        print(output)

        #/* (4) */
        email_report(
            subject='rsnapshot summary',
            message=output
        )

        #/* clean up */
        cmd_rm_r(DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE,
                 DEFAULT_RSNAPSHOT_INTERMEDIATE_ERROR_FILE, force=True)


if __name__ == '__main__':
    print(simple_argparse(rsnapshot_run, sys.argv[1:]))

