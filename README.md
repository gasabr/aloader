# aloader

Script downloads all attachments from your email (unseen messages) through IMAP4.

Usage:

1. `git clone http://github.com/gasabr/aloader.git`
2. create config.py with the following content:

```python
SERVER   = 'imap.google.com' # example for gmail
LOGIN    = 'your_email'
PASSWORD = 'your_password'

DOWNLOAD_FOLDER = 'relative path from current directory'
REPORT_FILE = 'default: report.json'
```

