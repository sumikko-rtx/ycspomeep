import os
import sys
import ctypes
from simple_argparse import simple_argparse


#
# checking if the user of a script has root-like privileges?
#
def check_if_root(raise_exception=True):

    #/* https://stackoverflow.com/questions/1026431/cross-platform-way-to-check-admin-rights-in-a-python-script-under-windows */
    user_is_root = True

    #/* for windows, use shell32.dll api: IsUserAnAdmin */
    if sys.platform == 'cygwin' or sys.platform == 'win32':

        #/* cygwin may fail while using ctypes.windll */
        dll = None
        try:
            dll = ctypes.windll.LoadLibrary('shell32.dll')

        except Exception as e:
            dll = ctypes.cdll.LoadLibrary('shell32.dll')

        user_is_root = bool(dll.IsUserAnAdmin() != 0)


    #/* for unik-like system: id = 0: it is a root user */
    else:
        user_is_root = bool(os.getuid() == 0)



    #/* raise exception if not root */
    if not user_is_root:

        if raise_exception:
            raise Exception("This program requires root privileges!!!")

    return user_is_root








if __name__ == "__main__":
    print(simple_argparse(check_if_root, sys.argv[1:]))
