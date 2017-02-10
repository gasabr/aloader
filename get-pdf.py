#!/usr/bin/env python3
''' Getcha ya own.

    Script to collect mail attachments matching regex in one folder.
    Usage:
        1. Fill config.py with your data.
        2. Run script
'''
from imaplib import IMAP4_SSL
import email
import re
import os       # to write path
import base64   # to decode messages
import sys      # for progress bar
import json     # to store user info

import config


def valid(filename):
    splitted = re.split(r'[\W+|_]', filename)

    print(splitted)

    if len(splitted) != 8:
        return False

    print('subject=', splitted[4])
    print('extension=', splitted[-1])

    pattern = re.compile(r'\w+_\d+_\d+_\w+_\w+_\d+_\d+.\w+')
 
    if pattern.match(filename.lower()) and \
            splitted[4] in config.ALLOWED_SUBJECTS and \
            splitted[-1] in config.ALLOWED_EXTENSIONS:
        return True
    else:
        return False


# Print iterations progress
def printProgress (iteration, total, prefix = '', suffix = '', decimals = 2, barLength = 100):
    ''' Call in a loop to create terminal progress bar

        :Args:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : number of decimals in percent complete (Int)
            barLength   - Optional  : character length of bar (Int)
    '''

    filledLength    = int(round(barLength * iteration / float(total)))
    percents        = round(100.00 * (iteration / float(total)), decimals)
    bar             = '█' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write('\n')
        sys.stdout.flush()


def setup_connection():
    ''' Setting up connection with IMAP server.

        Takes dict with server, username, password
        :Args:
            user    - Required  : all user data in (dict)

        :Returns:
            server (imaplib.IMAP4_SS): IMAP server
    '''
    server = IMAP4_SSL(config.SERVER)
    server.login(config.LOGIN, config.PASSWORD)
    # TODO: check what this line does
    server.select('inbox') 

    return server


def find_files(server, ids):
    ''' Finds messages containing pdf files in inbox.

        takes array of ids to check
        return list of messages's parts with pdf files inside
        :Args:
            server  - Requided  : conection to email account (imaplib.IMAP4_SLL)
            ids     - Required  : list of ids to check (list(Str))
    '''
    i = 0
    msgs_with_pdf = []
    printProgress(i, len(ids), suffix='emails checked', barLength=50)

    for msg_id in ids:
        result, data = server.fetch(msg_id, '(RFC822)') # get message body
        raw_email = data[0][1] # what is this?
        temp_msg = email.message_from_bytes(raw_email)

        print(temp_msg['From'])

        for part in temp_msg.walk():
            if part.get_content_type() in config.ALLOWED_MIME_TYPES:
                parsed_sender = re.split(r'[<|>]', temp_msg['From'])
                # FIXME: write more reliable email extractors
                msgs_with_pdf.append({
                        'sender': parsed_sender[-2],
                        'sender_name': parsed_sender[0].encode('UTF-8').decode('UTF-8'),
                        'part'  : part,
                    })

        i += 1
        printProgress(i, len(ids), suffix='emails checked', barLength=50)

    return msgs_with_pdf


def create_file(path, bytes_):
    ''' Creates pdf file in given derectory.

        :Args:
            path        - Required  : comlete path to folder (Str)
            pdf_bytes   - Required  : pdf file in bytes (bytes)
    '''

    file = open(path, 'w+b') # write as a binary file
    file.write(bytes_)
    file.close()
    print('file %s created succesfully' % path)
    return 0


def create_report(reports):
    ''' Logs all saved papers.

        Dumps information about successfully performed emails to
        the config.REPORT_FILE
    '''
    try:
        filename = config.REPORT_FILE
    except Exception as e:
        print('Please, define REPORT_FILE in `config.py`.')
        print('Report will be written in `/report.json`.')
        filename = 'report.json'

    with open(filename, 'w+') as fp:
        json.dump(reports, fp, ensure_ascii=False)


def main():
    server = setup_connection()

    result, data = server.search(None, 'UNSEEN')
    ids = data[0].split()

    if len(ids) == 0:
        print('No new messages')
        return 0

    # TODO Find messages with files
    msgs_with_pdf = find_files(server, ids)

    if len(msgs_with_pdf) == 0:
        print('no new files to download.')
        return 0

    log = {'Incorrect Mask' : [], 
           'No file': [], 
           'Created succesfully': []
          }
    created_files = []

    for msg in msgs_with_pdf:
        filename = msg['part'].get_filename()

        if not valid(filename):
            continue

        path = os.path.join(config.BASE_DIR, filename)

        bytes_ = msg['part'].get_payload(decode=True) # file in bytes
        
        try:
            create_file(path, bytes_)
        except FileNotFoundError as e:
            log['No file'].append(path)
        else:
            log['Created succesfully'].append(path)
            created_files.append({'sender'     : msg['sender'],
                                  'sender_name': msg['sender_name'],
                                  'filename'   : filename,
                                })

    # print log
    for key, value in log.items():
        print(key, ':', len(value))

    create_report(created_files)


if __name__ == '__main__':
    main()
