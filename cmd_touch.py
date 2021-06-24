#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from str_2_bool import str_2_bool
import os
import datetime
import re




#
# Run command:
# 
# touch <datetime> <input_filename1> <input_filename2> ...
#
# If datetime=None, assume datetime = datetime.datetime.now()
#
def cmd_touch(*files,
              change_access_time=False,  # -a
              no_create=False,  # -c
              datetime_=None,
              timestamp='',  # -t
              no_dereference=False,  # -h
              change_modification_time=False,  # -m
              reference='',
              time_='',
              ):


    #/* TODO sumikko: AAA */
    if isinstance(datetime_, str):
        datetime_ = datetime.datetime.fromisoformat(datetime_)

    change_access_time = str_2_bool(change_access_time)    
    no_create = str_2_bool(no_create)
    no_dereference = str_2_bool(no_dereference) 
    change_modification_time = str_2_bool(change_modification_time) 

    #/*---------------------------------------------------------------------*/
    
    #/* parse timestamp as: [[CC]YY]MMDDhhmm[.ss] */
    if timestamp:
        
        g = re.search(
            r'(?P<YY>(?P<CC>\d{2})?\d{2})(?P<MM>\d{2})(?P<DD>\d{2})(?P<hh>\d{2})(?P<mm>\d{2})(?:[.](?P<ss>\d{2}))?', timestamp)

        if not g:
            raise Exception('invalid timestamp string')

        #/* list named groups as dict */
        groupdict = g.groupdict()


        #/* parse CC */
        CC = groupdict.get('CC')


        #/* parse YY */
        YY = groupdict.get('YY')

        if YY:
            YY = int(YY)
            
            #/* add 19 or 20 if CC is not specified */
            if not CC:
                if YY >= 66 and YY <= 99:
                    YY = YY + 1900
                else:  # /* << 00-68 */
                    YY = YY + 2000


        #/* get MM */
        MM = groupdict.get('MM')
        if not MM:
            raise Exception('missing MM (month)')
        
        MM = int(MM)
        if MM < 1 or MM > 12:
            raise Exception('MM must be between 01 and 12')


        #/* get DD */
        DD = groupdict.get('DD')
        if not DD:
            raise Exception('missing DD (day)')
        
        DD = int(DD)
        if MM < 1 or MM > 31:
            raise Exception('DD must be between 01 and 31')
        

        #/* get hh */
        hh = groupdict.get('hh')
        if not hh:
            raise Exception('missing hh (hour)')

        hh = int(hh)
        if hh > 23:
            raise Exception('hh must be between 00 and 23')


        #/* get mm */
        mm = groupdict.get('mm')
        if not mm:
            raise Exception('missing mm (minute)')
        
        mm = int(mm)
        if mm > 59:
            raise Exception('mm must be between 00 and 59')
        
        
        #/* get ss */
        ss = groupdict.get('ss')
        if not ss:
            ss = '00'
        
        ss = int(ss)
        if ss > 59:
            raise Exception('ss must be between 00 and 59')


        #/* datetime_ is not constructed by those params */
        datetime_ = datetime.datetime(YY, MM, DD, hh, mm, ss)

    #/*---------------------------------------------------------------------*/
    
    #/* datetime_= None : assume datetime_ = time now */
    if not datetime_:
        datetime_ = datetime.datetime.now()
        
    #/*---------------------------------------------------------------------*/

    #/* By default: Update the access and modification times */
    if (not change_access_time) and (not change_modification_time):
        change_access_time = True
        change_modification_time = True
        
    #/*---------------------------------------------------------------------*/
    
    #/* set change_access_time and change_modification_time according to time_ */
    time_ = time_.lower()

    if time_ in ['access', 'atime', 'use']:
        change_access_time = True

    if time_ in ['modify', 'mtime']:
        change_modification_time = True

    #/*---------------------------------------------------------------------*/

    #/* --- the main program --- */
    for x in files:

        #/* if no_dereference=False, resolve link: x (output file) */
        if not no_dereference:
            x = os.path.realpath(x)
        
        #/* in case of file exists */
        try:

            #/* showing stat information of file */
            stinfo = os.stat(x)
            
            #/* must convert into epoch time
            # * stinfo.st_atime & stinfo.st_mtime are measured in epoch
            # */
            epoch = datetime_.timestamp()

            #/* the format of epoch must be: (access_time, modification_time) */
            utime_data = [stinfo.st_atime, stinfo.st_mtime]

            if change_modification_time:
                utime_data[1] = epoch

            if change_access_time:
                utime_data[0] = epoch

            #/* modifying atime and mtime */
            os.utime(x, utime_data)


        #/* in case of file not exists */
        except Exception as e:
            
            #/* A file x that does not exist is created empty,
            # * unless no_create or no_dereference is supplied.
            # */
            if no_create or no_dereference:
                pass
            
            else:
                
                #/* the only way to create empty file... */
                f = open(x, 'a+b')
                f.write(b'')
                f.close()
                
                
                
                
                
                
                
                
if __name__ == '__main__':
    print(simple_argparse(cmd_touch, sys.argv[1:]))
