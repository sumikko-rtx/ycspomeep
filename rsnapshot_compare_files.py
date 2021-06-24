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
    # * -i: itemized changes. see rsync(1) for details
    # * -n: dry run, don't make any changes on disk!!!
    # */
    rsync_switches = '-rcvin' if deeply else '-rtvin'

    for type_, srcdir, destdir, rsync_extra_params in backup_jobs:

        #/* destdir are relative to snapshot_root/alpha.0 */
        destdir = os.path.join(
            '{0}.0'.format(rsnapconfig_get_retain_levels(idx=0, include_snapshot_root=True)),
            destdir,
        )

        #/* for type_ = local, ssh and rsync, use them directly */
        return_code, output, unused, unused = system_cmd(
            *['rsync', '--out-format=%i %n',
                 rsync_switches, srcdir, destdir],
            raise_exception=False,
        )

        #/* look for the line: 'sending incremental file list' or 'receiving incremental file list' */
        output_lines = output.splitlines()

        if 'sending incremental file list' in output_lines or 'receiving incremental file list' in output_lines:

            #/* remove last 3 lines containing statistic information */
            for line in output_lines[0:-4]:

                tmp = line.split(None,1)

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
                # * on ssh, rsnapshot only receive file from remote host, so no '<'
                # * '>' represents file(s) is/are received from remote host
                # * 'c' represents fils(s) is/are created/changed from local host
                # * '*' represents extra file(s) in <snapshot_root> and is/are going to be deleted
                # * '.' represents file(s) content is/are not updated
                # */

                if itemized_changes[0] in ['*']:
                    files_removed.append(filename)

                elif itemized_changes[0] in ['>', 'c']:

                    #/* for created file, itemized_changes[2:] is set to both '+'
                    # * (there are 9 '+'s in total
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
