#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from system_cmd import system_cmd
from check_if_root import check_if_root








def update_from_pkgmgr(check_upgradable=False):

    #/* must be root */
    check_if_root()

    #/*---------------------------------------------------------------------*/

    #/* update software database */
    possible_cmds = [
        ['zypper', 'ref'],  # << zypper
        ['pacman', '-Sy'],  # << pacman
        ['apt', 'update'],  # << apt
        ['dnf', 'check-update'],  # << dnf
        ['yum', 'check-update'],  # << yum
        ['emerge', '--sync'],  # << portage
        ['nix-channel', '--upgrade'],  # << Nix
    ]
    
    rc = 0
    for cmd in possible_cmds:

        print('INFO: trying {0}'.format(cmd))
            
        rc, unused, unused, unused = system_cmd(
            cmd=cmd,
            raise_exception=False,
        )

        if rc == 0:
            print('INFO: software database updated')
            break
        
    if rc != 0:
        raise Exception('Cannot update software database!!! Your package manager may be improperly installed!!!')

    #/*---------------------------------------------------------------------*/
    
    #/* show updatable packages (check_upgradable=True) */
    if check_upgradable:
        
        possible_cmds = [
            ['zypper', 'lu'],  # << zypper
            ['pacman', '-Qu'],  # << pacman
            ['apt', 'list', '--upgradable'],  # << apt
            ['dnf', 'check-update'],  # << dnf
            ['yum', 'check-update'],  # << yum
            ['emerge',  '--update', '--pretend', '@world'],  # << portage
            ['nix-channel', '--upgrade', '&&', 'nix-env',
                '-u', '&&', 'nix-collect-garbage'],  # << Nix
        ]
        
        rc = 0
        for cmd in possible_cmds:
    
            print('INFO: trying {0}'.format(cmd))
                
            rc, output, unused, unused = system_cmd(
                cmd=cmd,
                raise_exception=False,
            )
    
            if rc == 0:
                print(output)
                break
            
        if rc != 0:
            raise Exception('Cannot list upgrade-able package(s)!!! Your package manager may be improperly installed!!!')

    #/*---------------------------------------------------------------------*/

    #/* install all upgrades (check_upgradable=False) */   
    else:
        
        possible_cmds = [
            ['zypper', '-n', 'up'],  # << zypper
            ['pacman', '--noconfirm', '-Syu'],  # << pacman
            ['apt', '-y', 'upgrade'],  # << apt
            ['dnf', '-y', 'update'],  # << dnf
            ['yum', '-y', 'update'],  # << yum
            ['emerge', '--update', '--deep', '--with-bdeps=y', '@world'],  # << portage
            ['nix-env', '-u', '&&', 'nix-collect-garbage'],  # << Nix
        ]

        rc = 0
        for cmd in possible_cmds:
    
            print('INFO: trying {0}'.format(cmd))
    
            rc, unused, unused, unused = system_cmd(
                cmd=cmd,
                raise_exception=False,
            )
    
            if rc == 0:
                print('INFO: packages are successfully updated!!!')
                break
            
        if rc != 0:
            raise Exception('Cannot install all upgrade-able package(s)!!! Your package manager may be improperly installed!!!')





if __name__ == '__main__':
    print(simple_argparse(update_from_pkgmgr, sys.argv[1:]))

