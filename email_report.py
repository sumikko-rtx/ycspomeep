#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from send_mail import send_mail
import os
import datetime
from cmd_touch import cmd_touch
from file_modified_since import file_modified_since
from constants import BACKUP_SERVER_NAME
from constants import SMTP_HOST, SMTP_PORT_NUMBER, SMTP_TRY_SSL_TLS,\
    SMTP_TIMEOUT_SECONDS, RECIPIENT_EMAILS, SENDER_EMAIL, SENDER_LOGIN_NAME,\
    SENDER_LOGIN_PASSWORD
from constants import TEMP_DIR

#/* a shortcut function to send mail by given sender mail account from configs/email_settings.py */
def email_report(subject='',
                 message='',
                 message_file='',
                 use_html_markup=False,
                 attach_files=[],
                 encoding='utf-8',
                 pidname='',
                 wait_interval_seconds=0,
                 ):

    #/* this control whether an email can be sent or not */
    can_sent_email = True

    if pidname:
        pidfile = '{0}.pid'.format(pidname)
        pidfile = os.path.join(TEMP_DIR, pidfile)
        pidfile = os.path.realpath(pidfile)

        try:
            duration_seconds = file_modified_since(pidfile)

        except Exception as e:
            #/* +inf */
            duration_seconds = sys.maxsize

        if wait_interval_seconds > 0 and duration_seconds >= wait_interval_seconds:
            pass
        else:
            can_sent_email = False

    #/*---------------------------------------------------------------------*/

    #print('can_sent_email:', can_sent_email)

    #/* send mail if can_sent_email=True */
    if can_sent_email:

        #/* ignore send mail errors */
        try:

            #/* subject must include backup server name and datetime now!!! */
            datetime_now = datetime.datetime.now()
            subject = '{0}: {1} ({2})'.format(
                BACKUP_SERVER_NAME, subject, datetime_now)

            #/* send email message*/
            send_mail(
                host=SMTP_HOST,
                port=SMTP_PORT_NUMBER,
                try_ssl_tls=SMTP_TRY_SSL_TLS,
                timeout=SMTP_TIMEOUT_SECONDS,
                recipient_addresses=RECIPIENT_EMAILS,
                sender_address=SENDER_EMAIL,
                sender_loginname=SENDER_LOGIN_NAME,
                sender_password=SENDER_LOGIN_PASSWORD,

                subject=subject,
                message=message,
                message_file=message_file,
                use_html_markup=use_html_markup,
                attach_files=attach_files,
                encoding=encoding,
            )

        except Exception as e:
            #print("WARINING: cannot sent email: {0}".format(e))
            pass

        #/* update pidfile's mtime, if any */
        if pidname:
            cmd_touch(pidfile, datetime_=datetime.datetime.now())


if __name__ == '__main__':
    print(simple_argparse(email_report, sys.argv[1:]))

