#/* hostname or ip address of a SMPT server
# */
SMTP_HOST = 'smtp.gmail.com'


#/* Port number to a SMPT server
# */
SMTP_PORT_NUMBER = 465


#/* True to use TLS or SSL encryption
# */
SMTP_TRY_SSL_TLS = True


#/* same as PLC_TIMEOUT_SECONDS */
#/* The time must be enough (but not too high) to send full backup log
# */
SMTP_TIMEOUT_SECONDS = 600


#/* Sender's email address
# */
SENDER_EMAIL = 'sender@gmail.com'  # <<<


#/* Login name to login sender's email accounts
# * (may not be same as SENDER_EMAIL)
# */
SENDER_LOGIN_NAME = 'sender@gmail.com'  # <<<

#/* Password to login sender's email accounts
# */
SENDER_LOGIN_PASSWORD = 'senderpassword'  # <<<


#/* List of the recipient's e-mail addresses
# */
RECIPIENT_EMAILS = [
    'recipient1@gmail.com',
    #'recipient2@gmail.com',  # <<< uncomment this line for the 2nd recipient
    #'recipient3@gmail.com',  # <<< uncomment this line for the 3rd recipient
    #'recipient4@gmail.com',  # <<< uncomment this line for the 4th recipient
]


#/* notify to RECIPIENT_EMAILS when disk have n% full
# *
# * -1 to un-set
# *
# * Note: this won't tell backup server error to PLC.
# */
#NOTIFY_MAX_DISK_USED_PERCENT = 80


#/* notify to RECIPIENT_EMAILS when disk temperature is not within
# * the safe limit, [NOTIFY_MIN_DISK_TEMP, NOTIFY_MAX_DISK_TEMP]
# *
# * Note: this won't tell backup server error to PLC.
# */
#NOTIFY_DISK_MIN_TEMP = 20
#NOTIFY_DISK_MAX_TEMP = 50


#/* notify to RECIPIENT_EMAILS when disk has reached at least n hours
# * (n = 0, 1, 2, ...)
# *
# * -1 to un-set.
# *
# * Note: this won't tell backup server error to PLC.
# */
#NOTIFY_DISK_MAX_POWER_ON_HOURS = 35040


#/* notify to RECIPIENT_EMAILS when disk has at least n (possible) bad sectors
# * (n = 0, 1, 2, ...)
# *
# * -1 to un-set.
# *
# * Note: this will tell backup server error to PLC and stop all existing backup jobs.
# */
#NOTIFY_DISK_MAX_BAD_SECTORS = 1024


#/* If set to True,
# * notify to RECIPIENT_EMAILS when backup was successfully completed
# */
#NOTIFY_BACKUP_SUCCESS = False  # <<<


#/* If set to True,
# * notify to RECIPIENT_EMAILS when backup was failed or interrupted by user
# */
#NOTIFY_BACKUP_FAILED = True  # <<<


#/* If set to True,
# * notify to RECIPIENT_EMAILS when backup was run by user
# */
#NOTIFY_MANUAL = False


#/* If set to True,
# * notify to RECIPIENT_EMAILS when backup was run by cron / python3-schedule
# */
#NOTIFY_AUTO = False


#/* notify when at least n files copied (n = 0, 1, 2, ...)
# *
# * -1 to un-set.
# */
#NOTIFY_MIN_FILE_TRANSFERRED = -1


#/* notify when at least n bytes copied (n = 0, 1, 2, ...)
# *
# * -1 to un-set.
# */
#NOTIFY_MIN_BYTES_TRANSFERRED = -1


#/* notify when backup duration at least n second (n = 0, 1, 2, ...)
# *
# * -1 to un-set.
# *
# * when backup duration >= NOTIFY_SOFT_BACKUP_SECONDS_LIMIT:
# *   give warning
# *
# * when backup duration >= NOTIFY_HARD_BACKUP_SECONDS_LIMIT:
# *   backup exceeds that limit and stop the file backup
# *   (this will treat it as backup failed)
# *
# * NOTIFY_SOFT_BACKUP_SECONDS_LIMIT must be less than NOTIFY_HARD_BACKUP_SECONDS_LIMIT
# * otherwise un-set.
# *
# * note: 1 hour    = 3600 seconds
# *       1 minutes = 60 seconds
# */
#NOTIFY_SOFT_BACKUP_SECONDS_LIMIT = 9*3600  # <<<
#NOTIFY_HARD_BACKUP_SECONDS_LIMIT = 18*3600  # <<<

