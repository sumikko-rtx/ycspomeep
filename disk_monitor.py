#!/usr/bin/env python3
import sys
from smart_scan_open import smart_scan_open
from simple_argparse import simple_argparse
from str_2_bool import str_2_bool
from disk_check_bad_sectors import disk_check_bad_sectors
from disk_check_smart_attributes import disk_check_smart_attributes
from disk_check_temperature import disk_check_temperature
from disk_check_power_on_hours import disk_check_power_on_hours
from plc_report import plc_report
from email_report2 import email_report2
from smart_self_test import smart_self_test
import time
from constants import NOTIFY_DISK_MAX_BAD_SECTORS,\
    NOTIFY_DISK_MIN_TEMP, NOTIFY_DISK_MAX_TEMP, NOTIFY_DISK_MAX_POWER_ON_HOURS
from constants import PLC_RWADDR_SERVER_STATUS,\
    PLC_RWCODE_SERVER_STATUS_OK, PLC_RWCODE_SERVER_STATUS_FAILED
from disk_isolate_offline import disk_isolate_offline
from disk_isolate_online import disk_isolate_online


#/* return disk model name string */
def __get_disk_model_string(disk):

    #/* model_family may not defined, use get instead of __getitem__ */
    return "{0} {1} {2} (serial_number={3})".format(
        disk.get("model_family", ""),
        disk.get("device_model", ""),
        disk.get("firmware_version", ""),
        disk.get("serial_number", ""),
        #disk.get("device_filename", ""),
        #disk.get("device_type", ""),
    )


def disk_monitor(negate=False):

    negate = str_2_bool(negate)
    warning_msgs = []
    error_msgs = []
    disks = []
    
    #/*---------------------------------------------------------------------*/
    
    #/* turn on the backup disk if any */
    try:
        disk_isolate_online()
        
    except Exception as e:
        warning_msgs.append('cannot turn on the backup disk(s) for health check: {0}'.format(str(e)))

    #/*---------------------------------------------------------------------*/

    #/* smart_scan_open and smart_self_test may raise SystemCmdException
    # * if smartctl encountered an error
    # */
    try:

        #/* list attached disks */
        disks = smart_scan_open()

        #/* do self test first */
        for j, x in enumerate(disks):

            #/* always run short test */
            smart_self_test(
                device_filename=x['device_filename'],
                device_type=x['device_type'],
                short=True,
                long=False,
            )

        #/* then check if all disks has finished short self-test */
        percentage_overall = 0
        while len(disks) > 0:

            tmp_percentage = 0
            for j, x in enumerate(disks):

                unused, percentage = smart_self_test(
                    device_filename=x['device_filename'],
                    device_type=x['device_type'],
                    print_progress=True,
                )

                tmp_percentage = tmp_percentage + percentage

                if percentage < 100:
                    print('[{0:6.2f}%] running a smart self-test for disk {1} of {2}: {3}'.format(
                        percentage_overall,
                        j + 1,
                        len(disks),
                        __get_disk_model_string(x),
                    ))

            #/* average progress% */
            percentage_overall = tmp_percentage / len(disks)

            #/* stop the loop if completed */
            if percentage_overall >= 100:
                break

            #/* To minimize CPU time... */
            time.sleep(1)

    #/* handle for CTRL+C interrupt: stop running smart test */
    except KeyboardInterrupt as e:

        warning_msgs.append('disk health check was interrupted by user')

        #/* abort all disk test... */
        for j, x in enumerate(disks):
            smart_self_test(
                device_filename=x['device_filename'],
                device_type=x['device_type'],
                abort_test=True,
                long=False,
            )

    except Exception as e:
        pass

    #/*---------------------------------------------------------------------*/

    #/* --- disk_check_smart_attributes --- */

    problem_disks = disk_check_smart_attributes(
        preload_disks=disks, negate=negate)

    for x in problem_disks:

        #/* (j, smart_attributes_ok, attr_id, attr_name, attr_value, attr_thresh, attr_worst, attr_raw) */
        j = x[0]
        smart_attributes_ok = x[1]

        #/* is smartctl enountered an error? */
        if not smart_attributes_ok:
            error_msgs.append('{0}: cannot retrieve s.m.a.r.t. attributes!!! Try \'smartctl -A -d {2} -- {1}\' for details!!!'.format(
                __get_disk_model_string(disks[j]),
                disks[j]['device_filename'],
                disks[j]['device_type'],
            ))
            continue

        attr_id = x[2]
        attr_name = x[3]
        #attr_value = [4]
        #attr_worst = [5]
        #attr_raw = [6]

        error_msgs.append('{0}: s.m.a.r.t. status bad ({1}: {2})!!! backup and replace!!!'.format(
            __get_disk_model_string(disks[j]),
            attr_id,
            attr_name,
        ))

    #/*---------------------------------------------------------------------*/

    #/* --- disk_check_bad_sectors --- */

    problem_disks = disk_check_bad_sectors(
        preload_disks=disks, negate=negate)

    for x in problem_disks:

        #/* (j, smart_attributes_ok, possible_bad_sectors) */
        j = x[0]
        #smart_attributes_ok = x[1]
        possible_bad_sectors = x[2]

        error_msgs.append('{0}: possibly found over {1} bad sectors (current: {2})!!! backup and replace!!!'.format(
            __get_disk_model_string(disks[j]),
            NOTIFY_DISK_MAX_BAD_SECTORS,
            possible_bad_sectors,
        ))

    #/*---------------------------------------------------------------------*/

    #/* --- disk_check_temperature --- */

    problem_disks = disk_check_temperature(
        preload_disks=disks, negate=negate)

    for x in problem_disks:

        #/* (j, smart_attributes_ok, disk_temp) */

        j = x[0]
        #smart_attributes_ok = x[1]
        disk_temp = x[2]

        warning_msgs.append('{0}: outside the safe operating temperature limits ({1} - {2} deg C) (current: {3} deg C)!!!'.format(
            __get_disk_model_string(disks[j]),
            float(NOTIFY_DISK_MIN_TEMP),
            float(NOTIFY_DISK_MAX_TEMP),
            disk_temp,
        ))

    #/*---------------------------------------------------------------------*/

    #/* --- disk_check_power_on_hours --- */
    problem_disks = disk_check_power_on_hours(
        preload_disks=disks, negate=negate)

    for x in problem_disks:

        #/* (smart_attributes_ok, disk_power_on_hours) */
        j = x[0]
        #smart_attributes_ok = x[1]
        disk_power_on_hours = x[2]

        warning_msgs.append('{0}: reached the maximum power on hours of {1} hours (current: {2} hours)!!!'.format(
            __get_disk_model_string(disks[j]),
            float(NOTIFY_DISK_MAX_POWER_ON_HOURS),
            disk_power_on_hours,
        ))

    #/*---------------------------------------------------------------------*/

    #/* is any other critical smart attribute need to be test? */

    #/*---------------------------------------------------------------------*/

    #/* disk check complete, remove DEFAULT_DISK_CHECKING_LOCKFILE */
    if warning_msgs or error_msgs:
        pass
    else:
        print('INFO: all disk(s) is/are ok!!! continue to backup...')

    #/* turn off the backup disk if any */
    disk_isolate_offline()
    
    #/*---------------------------------------------------------------------*/

    #/* report to plc */
    if bool(error_msgs):
        plc_report(write_rw_values=[
                   PLC_RWADDR_SERVER_STATUS, PLC_RWCODE_SERVER_STATUS_FAILED])
    else:
        plc_report(write_rw_values=[
                   PLC_RWADDR_SERVER_STATUS, PLC_RWCODE_SERVER_STATUS_OK])

    #/*---------------------------------------------------------------------*/

    #/* report to email recipients */
    if bool(warning_msgs) or bool(error_msgs):
        email_report2(
            warning_msgs=warning_msgs,
            error_msgs=error_msgs,
        )


if __name__ == '__main__':
    print(simple_argparse(disk_monitor, sys.argv[1:]))

