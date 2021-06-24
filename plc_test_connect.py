#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from plc_report import plc_report
import time

from constants import PLC_RWADDR_BACKUP_STATUS, PLC_RWCODE_BACKUP_STATUS_OK,\
    PLC_RWCODE_BACKUP_STATUS_FAILED, PLC_RWCODE_BACKUP_STATUS_IN_PROGRESS

from constants import PLC_RWADDR_SERVER_STATUS, PLC_RWCODE_SERVER_STATUS_OK,\
    PLC_RWCODE_SERVER_STATUS_FAILED
from rsnapshot_monitor import rsnapshot_monitor




def plc_test():

    #/* duration of color transition in secs */
    transistion_seconds = 2

    #/* inform this server present */
    rsnapshot_monitor()

    #/*---------------------------------------------------------------------*/

    #/* PLC_RWADDR_BACKUP_STATUS */
    for x in [
        PLC_RWCODE_BACKUP_STATUS_OK,
        PLC_RWCODE_BACKUP_STATUS_IN_PROGRESS,
        PLC_RWCODE_BACKUP_STATUS_FAILED,
    ]:
        plc_report(write_rw_values=[PLC_RWADDR_BACKUP_STATUS, x])
        time.sleep(transistion_seconds)

    #/*---------------------------------------------------------------------*/

    #/* PLC_RWADDR_SERVER_STATUS_STATUS */
    for x in [
        #PLC_RWCODE_SERVER_STATUS_OK,
        PLC_RWCODE_SERVER_STATUS_FAILED,
    ]:
        plc_report(write_rw_values=[PLC_RWADDR_SERVER_STATUS, x])
        time.sleep(transistion_seconds)


    #/*---------------------------------------------------------------------*/

    #/* reset everything */
    plc_report(write_rw_values=[
               PLC_RWADDR_BACKUP_STATUS, PLC_RWCODE_BACKUP_STATUS_OK])
    
    plc_report(write_rw_values=[
               PLC_RWADDR_SERVER_STATUS, PLC_RWCODE_SERVER_STATUS_OK])



if __name__ == '__main__':
    print(simple_argparse(plc_test, sys.argv[1:]))
