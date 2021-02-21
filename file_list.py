#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
import os
import re
from str_2_bool import str_2_bool


#/**
# *  Main entry function
# */
def file_list(*dirs,
              list_files=False,
              list_directories=False,
              list_symlinks=False,
              min_filesize=0,
              max_filesize=-1,
              recurse=False,
              max_recurse_level=999,
              current_recurse_level=0,
              regex='',
              ):

    list_files = str_2_bool(list_files)
    list_directories = str_2_bool(list_directories)
    list_symlinks = str_2_bool(list_symlinks)
    min_filesize = int(min_filesize)
    max_filesize = int(max_filesize)
    recurse = str_2_bool(recurse)
    max_recurse_level = int(max_recurse_level)
    current_recurse_level = int(current_recurse_level)

    #/************************************************************************/

    output_files = []

    #/* input directories are in parsed_args.dirs */
    for d in dirs:

        #/* canonicalise input file path */
        d = os.path.realpath(d)

        #/* PermissionError: when reading locked directory(s) */
        try:
            items = os.listdir(d)
        except PermissionError as e:
            print('WARNING: {0}'.format(e))
            continue

        #/* selectively output file contents... */
        for item in items:

            #/* full path of item */
            item_fullpath = os.path.join(d, item)

            #/* item is a link, but not link */
            if os.path.islink(item_fullpath):
                if list_symlinks:
                    output_files.append(item_fullpath)
                continue

            #/* filter by filesize */
            #/* os.path.getsize(item_fullpath) cannot be used for link */
            filesize = os.path.getsize(item_fullpath)
            if filesize < min_filesize or (max_filesize > 0 and filesize > max_filesize):
                continue

            #/* filter by regex */
            if not re.search(regex, item_fullpath):
                continue

            #/* item is a directory, but not link */
            if os.path.isdir(item_fullpath):

                #/* append to output_files if -d is used */
                if list_directories:
                    output_files += [item_fullpath]

                #/* -R / --recurese is used */
                if recurse:

                    #/* recurse level +1 */
                    current_recurse_level = current_recurse_level + 1

                    #/* Reach maximum level? */
                    if current_recurse_level < max_recurse_level:

                        tmp = file_list(item_fullpath,
                                        list_files=list_files,
                                        list_directories=list_directories,
                                        list_symlinks=list_symlinks,
                                        min_filesize=min_filesize,
                                        max_filesize=max_filesize,
                                        recurse=True,
                                        max_recurse_level=max_recurse_level,
                                        current_recurse_level=current_recurse_level,
                                        regex=regex,
                                        )

                        output_files.extend(tmp)

                    #/* searching complete. */
                    #/* recurse level -1 */
                    current_recurse_level = current_recurse_level - 1

            #/* item is a file, but not link */
            elif os.path.isfile(item_fullpath):

                #/* append to output_files if -f is used */
                if list_files:
                    output_files.append(item_fullpath)

    #/* sort the output list and print */
    #?* the returned filename are absoulute */
    output_files.sort()
    return output_files


if __name__ == "__main__":
    print(simple_argparse(file_list, sys.argv[1:]))
