#!/usr/bin/env python3
import sys
import os
from simple_argparse import simple_argparse
from str_2_bool import str_2_bool
import re

#/* TODO sumikko: VVV */
__verbose_level = 0
def __verbose(*msg, sep=',', end='\n', level=0):
    if __verbose_level >= level:
        print(*msg, sep=sep, end=end)
        
        
        
        
        
        
        
        
def __mkdir(dir_, mode, skip_existing=False):

    try:      
        os.mkdir(dir_, mode)
        __verbose('created directory: {0}'.format(dir_), level=1)

    except FileExistsError as e:
        if not skip_existing:
            raise e from None

    except Exception as e:
        raise e from None








def cmd_mkdir(*dirs,
              mode=0o777, # -m
              parents=False, # -p
              verbose=False,  # -v
              sep=',',
              # -Z
              # --context
              ):

    #/* TODO sumikko: AAA */
    if not isinstance(mode, int):
        mode = int(mode, 8)

    parents = str_2_bool(parents)
    
    
    #/* TODO sumikko: VVV */
    verbose = str_2_bool(verbose)
    global __verbose_level
    __verbose_level = 1 if verbose else 0

    #/*---------------------------------------------------------------------*/

    #/* --- the main program --- */
    for x in dirs:

        #/* if parents=True, behave os.makedirs */
        if parents:

            target_path = ''
            
            #/* on windows, x_drive will be set like C: ... */
            x_drive, x_tail = os.path.splitdrive(x)
            
            components = re.split(r'[/\\]', x_tail)
            
            for j, y in enumerate(components):

                #/* construct the first path component... */
                if j == 0:
                    
                    #/* window */
                    if x_drive:
                        target_path = os.path.join(x_drive, y)

                    #/* unix like */
                    else:
                        target_path = os.path.join(os.sep, y)
                
                
                #/* construct the remaining path components...  */
                else:
                    target_path = os.path.join(target_path, y)

                #/* try os.mkdir */
                __mkdir(target_path, mode, skip_existing=True)


            
            
        #/* otherwise, use os.mkdir directory */ 
        else:
            __mkdir(x, mode)







if __name__ == '__main__':
    print(simple_argparse(cmd_mkdir, sys.argv[1:]))
