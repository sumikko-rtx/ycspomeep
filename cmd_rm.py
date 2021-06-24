#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
from str_2_bool import str_2_bool
from file_list import file_list





#/* TODO sumikko: VVV */
__verbose_level = 0
def __verbose(*msg, sep=',', end='\n', level=0):
    if __verbose_level >= level:
        print(*msg, sep=sep, end=end)





#/* TODO sumikko: JJJ */
def __input():
    
    #/* python3 */
    if sys.hexversion >= 0x03000000:
        return input()
    
    #/* python2 */
    else:
        return raw_input()






# TODO 1. no_preserve_root not yet completed
#         if unless no_preserve_root=True, cmd_rm won't delete /.
#
#      2. os.path.ismount('/') = True!!!
#         os.path.ismount('c:') = True!!!

# TODO preserve_root not yet completed
#
# rm -ri /
# rm: it is dangerous to operate recursively on '/'
# rm: use --no-preserve-root to override this failsafe
#

def cmd_rm(*files,
             force=False, # -f
             prompt_every_removal=False, # -i
             prompt_3_files_removal=False, # -I
             interactive='never',
             one_file_system=False,
             no_preserve_root=False,
             preserve_root='all',
             recursive=False, # -R
             recursive2=False, # -r
             dir_=False, # -d
             verbose=False, # -v
             ):
    
    #/* TODO sumikko: AAA */
    force = str_2_bool(force)    
    prompt_every_removal = str_2_bool(prompt_every_removal)
    prompt_3_files_removal = str_2_bool(prompt_3_files_removal) 
    one_file_system = str_2_bool(one_file_system) 
    no_preserve_root = str_2_bool(no_preserve_root)
    recursive = str_2_bool(recursive)
    recursive2 = str_2_bool(recursive2)
    dir_ = str_2_bool(dir_)

    
    #/* TODO sumikko: VVV */
    verbose = str_2_bool(verbose)
    global __verbose_level
    __verbose_level = 1 if verbose else 0

    #/*---------------------------------------------------------------------*/

    #/* recursive=True or recursive2=True:
    # * remove directories and their contents recursively
    # */
    if recursive or recursive2:
        dir_ = True

    #/*---------------------------------------------------------------------*/
    
    #/* set prompt_every_removal and prompt_3_files_removal according to interactive */
    interactive = interactive.lower()

    if interactive in ['never']:
        pass

    elif interactive in ['once']:
        prompt_3_files_removal = True

    elif (not interactive) or interactive in ['always']:
        prompt_every_removal = True

    else:
        raise Exception('invalid interactive: {0}'.format(interactive))
    
    #/*---------------------------------------------------------------------*/

    #/* force=True, never prompt */
    if force:
        prompt_every_removal = False
        prompt_3_files_removal = False
        
    #/*---------------------------------------------------------------------*/

    #/* --- the main program --- */
    for j, x in enumerate(files):
        
        #/* True to prompt before every removal */
        promt_removal = False
        
        #/* True to confirm delete file */
        confirm_2_delete = True
        
        #/* Trigger prompt_every_removal */
        if prompt_every_removal:
            promt_removal = True

        #/* Trigger prompt_3_files_removal */
        if prompt_every_removal and j >= 2:
            promt_removal = True
            
            


        #/* one_file_system=True, do not cross any file system */
        if one_file_system and os.path.ismount(x):
            continue
            
        #/* in case of directory... */
        if os.path.isdir(x) and (not os.path.islink(x)):

            #/* recursive or recursive2 is used */
            if recursive or recursive2:

                if promt_removal:
                    __verbose('''descend into directory '{0}'?'''.format(x), level=0)
                    confirm_2_delete = str_2_bool(__input())
                 
                if confirm_2_delete:
                    
                    #/* list files in subdirectory and recursively calls cmd_rm */
                    files_in_subdir = file_list(x,
                                                list_files=True,
                                                list_directories=True,
                                                list_symlinks=True,
                                                )

                    for y in files_in_subdir:
                        cmd_rm(y,
                               force=force,
                               prompt_every_removal=promt_removal,  # /* << keep prmpting */
                               prompt_3_files_removal=False,
                               interactive='never',
                               one_file_system=one_file_system,
                               no_preserve_root=no_preserve_root,
                               preserve_root=preserve_root,
                               recursive=True,
                               recursive2=True,
                               dir_=True,
                               verbose=verbose,
                               )






            #/* if user says no about descend into directory
            # * don't prompt directory deletion
            # */
            if confirm_2_delete and promt_removal and dir_:
                __verbose('''remove directory '{0}'?'''.format(x), level=0)
                confirm_2_delete = str_2_bool(__input())
                
            #/* use os.rmdir to remove (empty) directory(ies) */
            if confirm_2_delete:

                #/* dir_ option must be use */
                if dir_:
                    
                    try:
                        os.rmdir(x)
                        __verbose('''removed directory '{0}' '''.format(x), level=1)
                        
                    except Exception as e:
                        if not force:
                            raise e from None

                else:
                    os.remove(x)  # /* << trap to fail!!! */





        #/* in case of file or link... */
        else:
            
            if promt_removal:
                __verbose('''remove file '{0}'?'''.format(x), level=0)
                confirm_2_delete = str_2_bool(__input())
            
            #/* use os.remove to remove file(s) or link(s) */
            if confirm_2_delete:
                
                try:
                    os.remove(x)
                    __verbose('''removed file '{0}' '''.format(x), level=1)
                    
                except Exception as e:
                    if not force:
                        raise e from None





# sumikko_block_diagram_init(__main__, ...)



if __name__ == '__main__':
    print(simple_argparse(cmd_rm, sys.argv[1:]))
