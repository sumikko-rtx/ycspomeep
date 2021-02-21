#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import psutil
from rsnapconfig_get_snapshot_root import rsnapconfig_get_snapshot_root
from configs.email_settings import NOTIFY_MAX_DISK_USED_PERCENT


#/* check disk usage from snapshot_root, which defined in given rsnapshot config file
# * if there was an error while reading snapshot_root, this will return all zero values
# */
def rsnapshot_check_snapshot_root_usage(negate=False):

    #/* from rsnapshot config file */
    snapshot_root = rsnapconfig_get_snapshot_root()

    #/* True if snapshot_root exists */
    have_snapshot_root_exist = False

    #/* True if snapshot_root have not enough disk space */
    have_low_disk_space = False

    #/*---------------------------------------------------------------------*/

    #/* this store all disk warning, used to prepare an email message */
    current_disk_warnings = []

    try:
        
        #/* Exception when try to show disk usage on unmounting disk */
        tmp = psutil.disk_usage(snapshot_root)

        bytes_used = tmp.used
        bytes_free = tmp.free
        bytes_total = bytes_used + bytes_free
        percent_used = 100.0 * float(bytes_used) / float(bytes_total)
        #percent_free = 100.0 * float(bytes_free) / float(bytes_total)
        percent_free = 100.0 - percent_used

    #/* in case psutil encountered an error */
    except Exception as e:

        #/* assume all value as zero */
        bytes_used = 0
        bytes_free = 0
        bytes_total = 0
        percent_used = 0.0
        percent_free = 0.0

    #/*---------------------------------------------------------------------*/

    #/* test... */
    condition = (percent_used >= NOTIFY_MAX_DISK_USED_PERCENT)

    if negate:
        condition = (not condition)

    if condition:
        have_low_disk_space = True

    #/* --- return 6 values --- */
    return have_snapshot_root_exist, have_low_disk_space, bytes_used, bytes_free, bytes_total, percent_used, percent_free


if __name__ == '__main__':
    print(simple_argparse(rsnapshot_check_snapshot_root_usage, sys.argv[1:]))
