#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from system_cmd import system_cmd
import os
from cmd_rm_r import cmd_rm_r
from constants import TEMP_DIR, CURRENT_VERSION


def update_from_git(url='https://github.com/sumikko-rtx/ycspomeep.git',
                    branch='main',
                    to_target_version='',
                    check_new_version=False):

    #/*---------------------------------------------------------------------*/

    #/* note: the following procedures requires git */

    #/* tmp directory stores the git-cloned data */
    ycspomeep_at_tmpdir = os.path.join(TEMP_DIR, 'plc_ycspomeep_git_repository')
    ycspomeep_at_tmpdir = os.path.realpath(ycspomeep_at_tmpdir)

    #/* git refuses cloning if ycspomeep_at_tmpdir is not empty */
    cmd_rm_r(ycspomeep_at_tmpdir, force=True)
    os.makedirs(ycspomeep_at_tmpdir)

    #/* get from github repository */
    unused, unused, unused, unused = system_cmd(
        cmd=[
            'git', 'clone',
            '--branch', branch,
            url,
            ycspomeep_at_tmpdir
        ],
        cwd=TEMP_DIR,
    )

    #/* repository name must be ycspomeep.git */
    unused, output, unused, unused = system_cmd(
        cmd=[
            'git', 'remote', 'get-url', 'origin',
        ],
        cwd=ycspomeep_at_tmpdir,
    )

    if not output.endswith('/ycspomeep.git'):
        raise Exception(
            'not a valid ycspomeep repository')

    #/* load update history */
    unused, unused, unused, unused = system_cmd(
        cmd=['git', 'fetch'],
        cwd=ycspomeep_at_tmpdir,
        raise_exception=True,
    )
    
    #/* get the latest version */
    unused, git_output, unused, unused = system_cmd(
        cmd=['git', 'tag', '--sort=-taggerdate'],
        cwd=ycspomeep_at_tmpdir,
    )

    #/* get the first line form the last git_output */
    if not to_target_version:
            
        to_target_version = ''
        tmp = git_output.splitlines()
    
        if tmp:
            to_target_version = tmp[0]
    
        else:
            raise Exception(
                'git was worked properly but empty version string returned.')

    #/* is that the latest version? */
    have_new_version = (CURRENT_VERSION != to_target_version)

    #/*---------------------------------------------------------------------*/

    #/* show the release information: git show <version> */
    if check_new_version:

        print('''The current version of ycspomeep is {0}!'''.format(
            CURRENT_VERSION))


        if have_new_version:

            print('''
The new version of ycspomeep {0} has been released!

You can download this version using the following git command(s):

    git clone --branch {1} {2}
    git checkout {0}
    
'''.format(
                to_target_version, branch, url
            ))

        else:

            print('''
This currently the newest version available.
                  ''')
            
        return None

    #/*---------------------------------------------------------------------*/

    #/* Otherwise, do automatic update
    # *
    # * (1) git checkout <to_target_version>
    # *
    # * (2) rsync -av --delete 
    # *         --exclude configs/ --exclude .git/ --exclude update.py
    # *         <ycspomeep_at_tmpdir>/ <this_py_dir>/
    # */

    unused, unused, unused, unused = system_cmd(
        cmd=['git', 'checkout', to_target_version],
        cwd=ycspomeep_at_tmpdir,
        raise_exception=True,
    )

    this_py_file = os.path.basename(__file__)
    this_py_dir = os.path.realpath(os.path.dirname(__file__))
    #this_py_dir = PROGRAM_DIR

    cmd = [
        'rsync', '-avn',
        '--exclude', '.git/',
        '--exclude', 'configs/',
        '--exclude', this_py_file,
        '{0}/'.format(ycspomeep_at_tmpdir),
        '{0}/'.format(this_py_dir),
    ]

    unused, output, unused, unused = system_cmd(
        cmd=cmd,
        cwd=ycspomeep_at_tmpdir,
        raise_exception=True,
    )

    #print(output)
    

if __name__ == '__main__':
    print(simple_argparse(update_from_git, sys.argv[1:]))
