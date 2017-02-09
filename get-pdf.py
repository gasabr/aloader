from imaplib import IMAP4, IMAP4_SSL
import email
import os       # to write path
import base64   # to decode messages
import sys      # for progress bar
import json     # to store user info


# Print iterations progress
def printProgress (iteration, total, prefix = '', suffix = '', decimals = 2, barLength = 100):
    """ Call in a loop to create terminal progress bar

        :Args:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : number of decimals in percent complete (Int)
            barLength   - Optional  : character length of bar (Int)
    """

    filledLength    = int(round(barLength * iteration / float(total)))
    percents        = round(100.00 * (iteration / float(total)), decimals)
    bar             = '█' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    sys.stdout.flush()
    if iteration == total:
        sys.stdout.write('\n')
        sys.stdout.flush()


def setup_connection(user):
    ''' Setting up connection with IMAP server.

        Takes dict with server, username, password
        :Args:
            user    - Required  : all user data in (dict)

        :Returns:
            server (imaplib.IMAP4_SS): IMAP server
    '''
    server = IMAP4_SSL(user['server'])
    server.login(user['login'], user['password'])
    a = server.list()

    print(a)

    server.select('inbox')

    return server


def find_pdf(server, ids):
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

        for part in temp_msg.walk():
            if part.get_content_type() == 'application/pdf':
                msgs_with_pdf.append(part)

        i += 1
        printProgress(i, len(ids), suffix='emails checked', barLength=50)

    return msgs_with_pdf


def create_file(path, pdf_bytes):
    """ Creates pdf file in given derectory.

        :Args:
            path        - Required  : comlete path to folder (Str)
            pdf_bytes   - Required  : pdf file in bytes (bytes)
    """
    
    file = open(path, 'w+b') # write as a binary file
    file.write(df_bytes)
    file.close()
    print('file %s created succesfully' % path)
    return 0


def create_path(fullname, base_dir):
    ''' Gets file name from email message.

        checks it for matching mask
        :Args:
            fullname (str)  - Required  : complete filename from email 
            base_dir (str)  - Required  : directory where are all files 

        :Returns:
            path (str): path to save file
    '''

    p = fullname.split('_')
    if len(p) == 1: # if there is no _ in filename
        raise ValueError

    path = base_dir
    for i in range(len(p)):
        path = os.path.join(path, p[i])

    return path


def main():
    # load users info from file
    with open('users.json') as users:
        users_data = json.load(users)

    # show available accounts
    print('Choose accout to connect or create new:')
    i = 0
    for key, value in users_data.items(): 
        for acc in value:
            i += 1
            print('\t', i, acc['name'])
    print('\t', i+1, 'Create acc')

    user_index = 0
    user = users_data['accounts'][user_index]

    server = setup_connection(user)

    result, data = server.search(None, 'UNSEEN')
    ids = data[0].split()

    if len(ids) == 0:
        print( 'No new messages')
        return 0

    msgs_with_pdf = find_pdf(server, ids)

    if len(msgs_with_pdf) == 0:
        print( 'no new files.')
        return 0

    base_dir = '' # read and store in file later

    log = {'Incorrect Mask' : [], 
           'No file': [], 
           'Created succesfully': []
          }

    for part in msgs_with_pdf:
        filename = part.get_filename()
        path = ''
        try:
            path = create_path(filename, base_dir)
        except ValueError:
            # obj.store(data[0].replace(' ',','),'+FLAGS','\Seen')
            # server.store( msg_id, '-FLAGS', '\Seen')
            log['Incorrect Mask'].append(path)
            continue

        pdf_b = part.get_payload(decode=True) # pdf in bytes
        
        try:
            create_file(path, pdf_b)
        except FileNotFoundError as e:
            log['No file'].append(path)
        else:
            log['Created succesfully'].append(path)

    # print log
    for key, value in log.items():
        print(key, ':', len(value))


if __name__ == '__main__':
    main()
