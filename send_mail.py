#!/usr/bin/env python3
import sys
from simple_argparse import simple_argparse
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
import ssl
from str_2_bool import str_2_bool

# for html_ecape function
from html import escape as html_escape # << python 3.2


def send_mail(host,
              recipient_addresses,
              port=465,
              try_ssl_tls=False,
              timeout=10.0,
              sender_address='',
              sender_loginname='',
              sender_password='',
              subject='',
              message='',
              message_file='',
              use_html_markup=False,
              attach_files=[],
              encoding='utf-8',
              sep=',',
              ):
    '''
    @description:
    Send an e-mail message.

    @param host@H: The hostname / ip address of a SMTP server.
    @param port@P: The port number to connect <host> (25, 465 or 587)
    @param recipient_addresses@r: The recipient's e-mail address(es) (can be used many times).
    @param try_ssl_tls@u: Try to establish secured SSL/TLS connection as possible.
    @param timeout@T: Timeout in seconds for blocking operations.
    @param sender_address@s: The sender's e-mail address.
    @param sender_loginname@l: The sender's login name.
    @param sender_password@p:The sender's login password (unsafe, use prompt_for_password instead).
    @param prompt_for_password@q: Provide a prompt for user password input.
    @param subject@t: The subject of an e-mail message.
    @param attach_files@a: Files to be attached into the receiver's e-mail message (can be used many times).
    @param message_file@f: Use whole text file content as <message>. If '-' is used, stdin will be used
    @param use_html_markup@k:Treat <message>as a html markup.
    @param encoding@E: Select for character encodings for reading/writing stdin, stdout or stderr.
    @param message@m: The email message.
    '''
    port = int(port)
    timeout = int(timeout)
    try_ssl_tls = str_2_bool(try_ssl_tls)

#     print('host',host)
#     print('recipient_addresses',recipient_addresses)
#     print('port',port)
#     print('try_ssl_tls',try_ssl_tls)
#     print('timeout',timeout)
#     print('sender_address',sender_address)
#     print('sender_loginname',sender_loginname)
#     print('sender_password',sender_password)
#     print('subject',subject)
#     print('attach_files',attach_files)
#     print('message_file',message_file)
#     print('use_html_markup',use_html_markup)
#     print('encoding',encoding)
#     print('message',message)
#     print('sep',sep)

    #/************************************************************************/

    #/* split recipient_addresses argument, if any */
    if isinstance(recipient_addresses, str):
        recipient_addresses = recipient_addresses.split(sep)
    recipient_addresses = list(recipient_addresses)

    #/* split attach_files argument, if any */
    if isinstance(attach_files, str):
        attach_files = attach_files.split(sep)
    attach_files = list(attach_files)

#     #/************************************************************************/
#
#     #/* check if host is valid */
#     host = CheckHostnameString.main(
#         host,
#     )
#
#     #/* check if port is valid */
#     port = CheckTcpPortNumber.main(
#         port,
#     )
#
#     #/* check if sender_address is valid */
#     sender_address = CheckEmailAddressString.main(
#         sender_address,
#     )
#
#     #/* check if recipient_addresses is valid */
#     for j in range(len(recipient_addresses)):
#         recipient_addresses[j] = CheckEmailAddressString.main(
#             recipient_addresses[j])
#
#     #/************************************************************************/

    #/* read text file as message */
    if message_file:

        try:

            #/* single dash: read from stdin */
            if message_file == '-':
                f = sys.stdin
                message = f.read()

            #/* otherwse read from a regular file*/
            else:
                with open(message_file, 'r') as f:
                    message = f.read()

        except Exception as e:

            print('WARNING: cannot no read file as message {0}: {1}'.format(
                message_file, str(e)))

        else:

            #/* use whole file content if file sucessfully read
            # * otherwise use message
            # */
            message = message

    #/************************************************************************/

    #/* try establish secured connection to SMTP server (SSL) */
    host_obj = None
    if try_ssl_tls:

        try:

            print('INFO: trying to establish secured connection (SSL) to SMTP server {0} (port {1})'.format(
                host,
                port,
            ))

            #/* TODO future version may use cert file to create ssl
            # * context
            # */
            context = ssl.create_default_context()
            host_obj = smtplib.SMTP_SSL(
                timeout=timeout,
                host=host,
                port=port,
                context=context
            )

        except Exception as e:
            host_obj = None
            print('INFO:  connection failed: {0}'.format(
                str(e)))

    #/************************************************************************/

    #/* try establish secured connection to SMTP server (TLS) */
    if not host_obj:

        try:

            print('INFO: trying to establish connection to SMTP server {0} (port {1})'.format(
                host,
                port,
            ))

            host_obj = smtplib.SMTP(
                timeout=timeout,
                host=host,
                port=port,
            )

            if try_ssl_tls:

                print('INFO: trying to establish TLS connection to SMTP server {0} (port {1})'.format(
                    host,
                    port,
                ))

                host_obj.ehlo()
                host_obj.starttls()

        except Exception as e:
            host_obj = None

            print('INFO:  connection failed: {0}'.format(
                str(e)))

    #/************************************************************************/

    #/* is that connection successfully established??? */
    if host_obj:
        print('INFO:  connection successfully established')

    else:

        raise Exception('Cannot connect to SMTP server {0}.'.format(
            host))

    #/************************************************************************/

    #/* send e-mail message goes here!!! */
    try:

        #/* only MIMEMultipart can handle multiple attachments */
        email_message = MIMEMultipart()

        #/* add sender email address to an e-mail message header 'From' */
        email_message['From'] = Header(sender_address, encoding)

        #/* add receiver email address(es) to an e-mail message header
        # * 'To'
        # *
        # * for 'To', address are separated by comma
        # */
        email_message['To'] = Header(
            ','.join(recipient_addresses),
            encoding,
        )

        #/* add subject (title) to an e-mail message header 'Subject' */
        email_message['Subject'] = Header(
            subject,
            encoding,
        )

        #/* Append email body
        # * we will use 'html' for both plain-text and html-markuped message
        # *
        # * Plain text message will encapsulated in <pre> tag so that
        # * it will be displayed in a fixed-width font, and the text preserves both spaces and line breaks. 
        # */
        if not use_html_markup:

            #/* message must be escaped from harmful characters such as
            # * &, >,...
            # */
            message = html_escape(message)
            message = '<pre>{0}</pre>'.format(message)

        part = MIMEText(message, 'html', encoding)
        email_message.attach(part)

        #/* attach file(s) to an email message */
        for x in attach_files:

            #/* Add file as application/octet-stream
            # * Email client can usually download this automatically as
            # * attachment
            # */
            try:

                #/* open each attached file (x) by binary mode */
                attached_file = open(x, 'rb')

                #/* put the opened file into payload */
                part = MIMEBase('application', 'octet-stream')
                part.set_payload((attached_file).read())

                #/* Encode the opened file contenct into base64 */
                encoders.encode_base64(part)

                #/* add payload header with filename */
                part.add_header('Content-Disposition', 'attachment',
                                filename=os.path.basename(x),
                                )

                #/* Add attachment to message and convert message to string */
                email_message.attach(part)

            except Exception as e:

                print('WARNING: cannot no read file as attachment {0}: {1}'.format(
                    x, str(e)
                ))

        #/* now the entire e-mail message is constructed */

        #/* try to login to the sender's e-mail account if any */
        if sender_loginname:

            #/* login to server as SENDER_LOGINNAME */
            print('INFO: log in as {0}'.format(
                sender_loginname
            ))

            host_obj.login(
                sender_loginname,
                sender_password,
            )

        #/* send the email message to receivers */
        print('INFO: sending an email message')

        host_obj.sendmail(
            sender_address,
            recipient_addresses,
            email_message.as_string(),
        )

        #/* terminate email session... */
        host_obj.quit()

    #/* handling send mail fail */
    except Exception as e:

        raise Exception(
            'Cannot sent an email message(s): {0}'.format(str(e)))

    #/* handling send mail success */
    else:
        print('SUCCESS: send mail success')

    return None   # CCCsumikko_func_end


if __name__ == '__main__':
    print(simple_argparse(send_mail, sys.argv[1:]))

