import os
import tempfile
import importlib


#/* These variables are technician use only */


#/* important: set the current ycspomeep program version here */
CURRENT_VERSION = "v2808b"

#/*---------------------------------------------------------------------*/

#/* This program root. */
PROGRAM_DIR = os.path.realpath(
    os.path.dirname(__file__)
)


#/* Directory storing config files. */
CONFIGS_DIR = os.path.realpath(
    os.path.join(PROGRAM_DIR, 'configs')
)


#/* System-independent temporary directory */
TEMP_DIR = os.path.realpath(
    tempfile.gettempdir()
)

#/*---------------------------------------------------------------------*/

#/* List of default search filenames. */

DEFAULT_RSNAPSHOT_CONFIG_FILE = os.path.realpath(
    os.path.join(CONFIGS_DIR, 'rsnapshot.cfg')
)

DEFAULT_PLC_SETTINGS_FILE = os.path.realpath(
    os.path.join(CONFIGS_DIR, 'plc_settings.update_from_git')
)

DEFAULT_EMAIL_SETTINGS_FILE = os.path.realpath(
    os.path.join(CONFIGS_DIR, 'email_settings.update_from_git')
)

DEFAULT_OTHER_SETTINGS_FILE = os.path.realpath(
    os.path.join(CONFIGS_DIR, 'other_settings.update_from_git')
)

DEFAULT_RSNAPSHOT_INTERMEDIATE_OUTPUT_FILE = os.path.realpath(
    os.path.join(TEMP_DIR, 'plc_rsnapshot_output.log')
)

DEFAULT_RSNAPSHOT_INTERMEDIATE_ERROR_FILE = os.path.realpath(
    os.path.join(TEMP_DIR, 'plc_rsnapshot_error.log')
)

DEFAULT_RSNAPSHOT_BACKUP_IN_PROGESS_LOCKFILE = os.path.realpath(
    os.path.join(TEMP_DIR, 'plc_rsnapshot_backup_in_progress.pid')
)






DEFAULT_DISK_CHECKING_LOCKFILE = os.path.realpath(
    os.path.join(TEMP_DIR, 'plc_disk_checking.pid')
)

DEFAULT_DISK_ERROR_LOCKFILE = os.path.realpath(
    os.path.join(TEMP_DIR, 'plc_disk_error.pid')
)


#/*---------------------------------------------------------------------*/


#/* --- default values from configs/email_settings.py --- */
try:
    x = importlib.import_module('configs.plc_settings')
except Exception as e:
    x = None


#/* name of this backup server
# * This will be shown on the email subject.
# */
BACKUP_SERVER_NAME = getattr(x, 'BACKUP_SERVER_NAME',
                             'MEEPMEEP')


#/* ip or hostname of a PLC
# */
PLC_HOST = getattr(x, 'PLC_HOST',
                   '192.168.1.51')


#/* Port number to a PLC (502)
# */
PLC_PORT_NUMBER = getattr(x, 'PLC_PORT_NUMBER',
                          502)


#/* Slave id for a PLC's Modbus protocal
# */
PLC_SLAVE_UNIT = getattr(x, 'PLC_SLAVE_UNIT',
                         1)


#/* max allowance time limit to connect a PLC, in seconds
# */
PLC_TIMEOUT_SECONDS = getattr(x, 'PLC_TIMEOUT_SECONDS',
                              10)


#/* The start address (0-indexed) of the LB coils
# * The end address will be set to PLC_RW_MIN - 1
# */
PLC_LB_MIN = getattr(x, 'PLC_LB_MIN',
                     0)


#/* The start end address (0-indexed) of the RB coils
# * The end address will be set to 65565
# */
PLC_RB_MIN = getattr(x, 'PLC_RB_MIN',
                     9999)


#/* The start address (0-indexed) of the LW holding registers
# * The end address will be set to PLC_RW_MIN - 1
# */
PLC_LW_MIN = getattr(x, 'PLC_LW_MIN',
                     0)


#/* The start end address (0-indexed) of the RW holding registers
# * The end address will be set to 65565
# */
PLC_RW_MIN = getattr(x, 'PLC_RW_MIN',
                     9999)


#/* list of backup status register address locations
# * these are relative to PLC_RW_MIN
# */
PLC_RWADDR_BACKUP_STATUS = getattr(x, 'PLC_RWADDR_BACKUP_STATUS',
                                   0)

PLC_RWADDR_SERVER_STATUS = getattr(x, 'PLC_RWADDR_SERVER_STATUS',
                                   1)


#/* list of backup status register address locations
# * these are relative to PLC_LB_MIN
# */
PLC_LBADDR_SERVER_PRESENCE_DETECT = getattr(x, 'PLC_LBADDR_SERVER_PRESENCE_DETECT',
                                            9)


#/* These values will be set to address PLC_RW_BACKUP_STATUS
# */
PLC_RWCODE_BACKUP_STATUS_OK = getattr(x, 'PLC_RWCODE_BACKUP_STATUS_OK',
                                      0)

PLC_RWCODE_BACKUP_STATUS_FAILED = getattr(x, 'PLC_RWCODE_BACKUP_STATUS_FAILED',
                                          1)

PLC_RWCODE_BACKUP_STATUS_IN_PROGRESS = getattr(x, 'PLC_RWCODE_BACKUP_STATUS_IN_PROGRESS',
                                               2)


#/* These values will be set to address PLC_RWADDR_SERVER_STATUS
# */
PLC_RWCODE_SERVER_STATUS_OK = getattr(x, 'PLC_RWCODE_SERVER_STATUS_OK',
                                      0)

PLC_RWCODE_SERVER_STATUS_FAILED = getattr(x, 'PLC_RWCODE_SERVER_STATUS_FAILED',
                                          1)


#/* These values will be set to address PLC_RWADDR_SERVER_PRESENCE_DETECT
# */
PLC_LBCODE_SERVER_PRESENT = getattr(x, 'PLC_LBCODE_SERVER_PRESENT',
                                    True)

PLC_LBCODE_SERVER_ABSENT = getattr(x, 'PLC_LBCODE_SERVER_ABSENT',
                                   False)



#/*---------------------------------------------------------------------*/

#/* --- default values from configs/email_settings.py --- */
try:
    x = importlib.import_module('configs.email_settings')
except Exception as e:
    x = None


#/* hostname or ip address of a SMPT server
# */
SMTP_HOST = getattr(x, 'SMTP_HOST',
                    'smtp.gmail.com')

#/* Port number to a SMPT server
# */
SMTP_PORT_NUMBER = getattr(x, 'SMTP_PORT_NUMBER',
                           465)

#/* True to use TLS or SSL encryption
# */
SMTP_TRY_SSL_TLS = getattr(x, 'SMTP_TRY_SSL_TLS',
                           True)

#/* same as PLC_TIMEOUT_SECONDS */
#/* The time must be enough (but not too high) to send full backup log
# */
SMTP_TIMEOUT_SECONDS = getattr(x, 'SMTP_TIMEOUT_SECONDS',
                               600)

#/* Sender's email address
# */
SENDER_EMAIL = getattr(x, 'SENDER_EMAIL', 'sender@gmail.com')

#/* Login name to login sender's email accounts
# * (may not be same as SENDER_EMAIL)
# */
SENDER_LOGIN_NAME = getattr(x, 'SENDER_LOGIN_NAME',     'sender@gmail.com')

#/* Password to login sender's email accounts
# */
SENDER_LOGIN_PASSWORD = getattr(x, 'SENDER_LOGIN_PASSWORD',
                                'senderpassword')

#/* List of the recipient's e-mail addresses
# */
RECIPIENT_EMAILS = getattr(x, 'RECIPIENT_EMAILS',
                           ['recipient1@gmail.com', 'recipient2@gmail.com', 'recipient3@gmail.com', 'recipient4@gmail.com'])

#/* notify to RECIPIENT_EMAILS when disk have n% full
# *
# * -1 to un-set
# *
# * Note: this won't tell backup server error to PLC.
# */
NOTIFY_MAX_DISK_USED_PERCENT = getattr(x, 'NOTIFY_MAX_DISK_USED_PERCENT',
                                       80)

#/* notify to RECIPIENT_EMAILS when disk temperature is not within
# * the safe limit, [NOTIFY_MIN_DISK_TEMP, NOTIFY_MAX_DISK_TEMP]
# *
# * Note: this won't tell backup server error to PLC.
# */
NOTIFY_DISK_MIN_TEMP = getattr(x, 'NOTIFY_DISK_MIN_TEMP',
                               20)

NOTIFY_DISK_MAX_TEMP = getattr(x, 'NOTIFY_DISK_MAX_TEMP',
                               50)

#/* notify to RECIPIENT_EMAILS when disk has reached at least n hours
# * (n = 0, 1, 2, ...)
# *
# * -1 to un-set.
# *
# * Note: this won't tell backup server error to PLC.
# */
NOTIFY_DISK_MAX_POWER_ON_HOURS = getattr(x, 'NOTIFY_DISK_MAX_POWER_ON_HOURS',
                                         35040)

#/* notify to RECIPIENT_EMAILS when disk has at least n (possible) bad sectors
# * (n = 0, 1, 2, ...)
# *
# * -1 to un-set.
# *
# * Note: this will tell backup server error to PLC.
# */
NOTIFY_DISK_MAX_BAD_SECTORS = getattr(x, 'NOTIFY_DISK_MAX_BAD_SECTORS',
                                      1024)

#/* notify when backup duration at least n second (n = 0, 1, 2, ...)
# *
# * -1 to un-set.
# *
# * when backup duration >= NOTIFY_SOFT_BACKUP_SECONDS_LIMIT:
# *   give warning
# *
# * when backup duration >= NOTIFY_HARD_BACKUP_SECONDS_LIMIT:
# *   backup exceeds that limit and stop the file backup
# *   (this will tell to PLC backup failed)
# *
# * NOTIFY_SOFT_BACKUP_SECONDS_LIMIT must be less than NOTIFY_HARD_BACKUP_SECONDS_LIMIT
# * otherwise un-set.
# *
# * note: 1 hour    = 3600 seconds
# *       1 minutes = 60 seconds
# */
NOTIFY_SOFT_BACKUP_SECONDS_LIMIT = getattr(x, 'NOTIFY_SOFT_BACKUP_SECONDS_LIMIT',
                                           9 * 3600)

NOTIFY_HARD_BACKUP_SECONDS_LIMIT = getattr(x, 'NOTIFY_HARD_BACKUP_SECONDS_LIMIT',
                                           18 * 3600)


#/* If sets to False, This will compare file(s) by check sum.
# * otherwise, by last modified time
# */
DEEPLY_COMPARE_FILES = getattr(x, 'DEEPLY_COMPARE_FILES',
                               False)


#/* notify when at least n file(s) is/are not successfully copied
# * (n = 0, 1, 2, ...)
# *
# * -1 to un-set.
# *
# * Note: this will tell to PLC backup failed
# */
NOTIFY_MAX_MISSING_FILES = getattr(x, 'NOTIFY_MAX_MISSING_FILES',
                                   1024)
