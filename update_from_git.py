#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from system_cmd import system_cmd
import os
from cmd_rm_r import cmd_rm_r
from constants import TEMP_DIR, CURRENT_VERSION
from cmd_mkdir import cmd_mkdir
from str_2_bool import str_2_bool


def update_from_git(url='https://github.com/sumikko-rtx/ycspomeep.git',
                    branch='main',
                    to_version='',
                    reset_configs=False,
                    check_new_version=False):

    #/* note: the following procedures requires git */
    check_new_version = str_2_bool(check_new_version)
    reset_configs = str_2_bool(reset_configs)
    
    
    #/* this script file and dir */
    this_py_file = os.path.basename(__file__)
    this_py_dir = os.path.realpath(os.path.dirname(__file__))
    #this_py_dir = PROGRAM_DIR


    #/* tmp directory stores the git-cloned data */
    ycspomeep_at_tmpdir = os.path.join(TEMP_DIR, 'plc_ycspomeep_git_repository')
    ycspomeep_at_tmpdir = os.path.realpath(ycspomeep_at_tmpdir)

    #/* git refuses cloning if ycspomeep_at_tmpdir is not empty */
    cmd_rm_r(ycspomeep_at_tmpdir, force=True)
    cmd_mkdir(ycspomeep_at_tmpdir, parents=True)
    #try:
    #    os.makedirs(ycspomeep_at_tmpdir)
    #except FileExistsError as e:
    #    pass
    
    #/* get from github repository */
    unused, unused, unused, unused = system_cmd(
        *[
            'git', 'clone',
            '--branch', branch,
            url,
            ycspomeep_at_tmpdir
        ],
        cwd=TEMP_DIR,
    )

    #/* repository name must be ycspomeep.git */
    unused, output, unused, unused = system_cmd(
        *['git', 'remote', 'get-url', 'origin',],
        cwd=ycspomeep_at_tmpdir,
    )

    if not output.endswith('/ycspomeep.git'):
        raise Exception(
            'not a valid ycspomeep repository')

    #/* load update history */
    unused, unused, unused, unused = system_cmd(
        *['git', 'fetch'],
        cwd=ycspomeep_at_tmpdir,
        raise_exception=True,
    )
    
    #/* get the latest version */
    #/* Note: -creatordate is more accurate than -taggerdate */
    unused, git_output, unused, unused = system_cmd(
        *['git', 'tag', '--sort=-creatordate'],
        cwd=ycspomeep_at_tmpdir,
    )

    #/* get the first line form the last git_output */
    if not to_version:
            
        to_version = ''
        tmp = git_output.splitlines()
    
        if tmp:
            to_version = tmp[0]
    
        else:
            raise Exception(
                'git was worked properly but empty version string returned.')

    #/* is that the latest version? */
    have_new_version = (CURRENT_VERSION != to_version)

    #/*---------------------------------------------------------------------*/

    #/* show the release information: git show <version> */
    if check_new_version:

        print('INFO: The current version of ycspomeep is {0}!'.format(
            CURRENT_VERSION))

        if have_new_version:

            print('INFO: The new version of ycspomeep {1} has been released!')
            print('INFO: You can upgrade to this version using the following command(s):') 
            print('''INFO: '{0}' '{1}' --to-version '{2}' --branch '{3}' --url '{4}' '''.format(
                sys.executable,
                this_py_file, 
                to_version, branch, url
            ))

        else:

            print('INFO: {0} is currently the newest version available.'.format(to_version))
            
        return None

    #/*---------------------------------------------------------------------*/

    #/* Otherwise, do automatic update
    # *
    # * (1) git checkout <to_version>
    # *
    # * (2) rsync -rv --delete 
    # *         --exclude configs/ --exclude .git/
    # *         <ycspomeep_at_tmpdir>/ <this_py_dir>/
    # */
    if have_new_version:
        
        unused, unused, unused, unused = system_cmd(
            *['git', 'checkout', to_version],
            cwd=ycspomeep_at_tmpdir,
            raise_exception=True,
        )

        cmd = [
            'rsync', '-rv', '--delete',
            '--exclude', 'configs/',
            '--exclude', '.git/',
            #'--exclude', this_py_file,
            '{0}/'.format(ycspomeep_at_tmpdir),
            '{0}/'.format(this_py_dir),
        ]

        unused, output, unused, unused = system_cmd(
            *cmd,
            cwd=ycspomeep_at_tmpdir,
            raise_exception=True,
        )
        
        print('INFO: ycspomeep has been successfully updated to version {0}!!!'.format(to_version))
    
    else:
        print('INFO: Your ycspomeep is already the newest version {0}!!! Nothing to do!!!'.format(to_version))
        
    #/*---------------------------------------------------------------------*/

    #/* if reset_configs = True
    # *
    # * (3) rsync -rv 
    # *         <ycspomeep_at_tmpdir>/configs/ <this_py_dir>/configs/
    # *
    # *     (if reset_configs = True)
    # */
    if reset_configs:
            
        cmd = [
            'rsync', '-rv',
            '{0}/configs/'.format(ycspomeep_at_tmpdir),
            '{0}/configs/'.format(this_py_dir),
        ]
        
        unused, output, unused, unused = system_cmd(
            *cmd,
            cwd=ycspomeep_at_tmpdir,
            raise_exception=True,
        )
        
        print('INFO: Your ycspomeep configuration has been reset to default!!!'.format(to_version))

if __name__ == '__main__':
    print(simple_argparse(update_from_git, sys.argv[1:]))

