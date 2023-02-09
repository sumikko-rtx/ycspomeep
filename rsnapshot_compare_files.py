#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
from rsnapconfig_getparam_backup import rsnapconfig_getparam_backup
from system_cmd import system_cmd
from rsnapconfig_get_retain_levels import rsnapconfig_get_retain_levels


#/* compare files in both souces dirs and <snapshot_root>
# */
def rsnapshot_compare_files(deeply=False):

    backup_jobs = rsnapconfig_getparam_backup()

    files_added = []
    files_modified = []
    files_removed = []

    #/* deeply_check=True, check file by checksum (-c)
    # * otherwise, check file by last modified time (-t)
    # *
    # * rsync_switches should be as same as rsnapshot's
    # * rsync_long_args and rsync_short_args
    # *
    # * -v: print running progress
    # * -i: itemized changes. see rsync(1) for details
    # * -n: dry run, don't make any changes on disk!!!
    # *
    # * -a = -rlptgoD (from rsync's man page)
    # */
    rsync_switches = '-WrlpcgoDvin' if deeply else '-WrlptgoDvin'
    #rsync_switches = '-cWavin --no-t' if deeply else '-Wavin'

    for type_, srcdir, destdir, rsync_extra_params in backup_jobs:
        
        #/* destdir are relative to snapshot_root/alpha.0 */
        destdir = os.path.join(
            '{0}.0'.format(rsnapconfig_get_retain_levels(idx=0, include_snapshot_root=True)),
            destdir,
        )

        #print('srcdir:', srcdir)
        #print('destdir:', destdir)

        #/* for type_ = local, ssh and rsync, use them directly */
        return_code, output, unused, unused = system_cmd(
            *['rsync', '--out-format=%i %n',
                 rsync_switches, destdir, srcdir],
            raise_exception=False,
        )

        #/* look for the line: 'sending incremental file list' or 'receiving incremental file list' */
        output_lines = output.splitlines()

        if 'sending incremental file list' in output_lines or 'receiving incremental file list' in output_lines:

            #/* remove last 3 lines containing statistic information */
            for line in output_lines[0:-4]:

                #/* output sample:
                # * >f.st...... iddd/logs/website-production-access_log
                # * >f.st...... iddd/web/website/production/shared/log/production.log
                # * .d..t...... iddd/web/website/production/shared/sessions/
                # * >f+++++++++ iddd/web/website/production/shared/sessions/ruby_sess.017a771cc19b18cd
                # * >f+++++++++ iddd/web/website/production/shared/session/
                # */
                tmp = line.split(None, 1)

                itemized_changes = tmp[0]
                filename = tmp[1]

                #/* itemized_changes[1]
                # *
                # * 'f' represents a regular file
                # * 'd' represents a directory
                # * 'L' represents a symlink
                # */
                if not itemized_changes[1] in ['f', 'L']:
                    continue

                #/* itemized_changes[0]
                # *
                # * on ssh, rsnapshot won't send file to remote host, so no '<'
                # *
                # * '>' represents file(s) is/are received from remote host
                # * 'c' represents file(s) is/are created/changed from local host
                # * '*' represents extra file(s) in <snapshot_root> and is/are going to be deleted
                # * '.' represents file(s) content is/are not updated
                # */

                if itemized_changes[0] in ['*']:
                    files_removed.append(filename)

                elif itemized_changes[0] in ['>', 'c']:

                    #/* for created file, itemized_changes[2:] is set to both '+'
                    # * (there are 9 '+'s in total)
                    # */
                    if itemized_changes[2:] == '+++++++++':
                        files_added.append(filename)
                    else:
                        files_modified.append(filename)

                else:
                    continue

    return files_added, files_modified, files_removed


if __name__ == '__main__':
#     files_added, files_modified, files_removed = rsnapshot_compare_files()
#     for x in files_added:
#         print('files_added',x)
#     for x in files_modified:
#         print('files_modified',x)
#     for x in files_removed:
#         print('files_removed',x)
    print(simple_argparse(rsnapshot_compare_files, sys.argv[1:]))
