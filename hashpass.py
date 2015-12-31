#!/usr/bin/env python
"""
Usage: hashpass [options] [<website>]

Options:
    -s --show    Display the site password instead of putting it in the clipboard
    -b --bcrypt  Use bcrypt as the hashing algorithm [Soon to be recommended]
    --sha        Use sha256 as the hashing algorithm [Default]
"""
from hashpasslib import *
import pinentry

import os.path, hashlib, getpass, sys
from docopt import docopt
import subprocess
import os

CLIP_SECONDS = 30

def init():
    """ Saves the master password to disk if you haven't already """
    if not read_stored_master():
        secret_master = getpass.getpass("No master password found. Enter one now: ")
        store_master(secret_master)
        print "Your master password will be hashed and saved at " + MASTER_PW_PATH

def get_password_cli(use_bcrypt):
    """ Gets the password via CLI and makes sure it matches the stored password """
    pw = getpass.getpass("Enter master password: ")
    while not is_correct_master(pw):
        print "That doesn't match the stored master."
        pw = getpass.getpass("Try again: ")
    use_master(pw, use_bcrypt)

def get_password(use_bcrypt):
    """ Gets the password via pinentry if possible. Fallback to CLI. """
    try:
        pw = pinentry.get_pin(description="Enter hashpass master password:",
                              prompt="Password:")
        while pw is None or not is_correct_master(pw):
            if pw == None:
                print "Bye."
                sys.exit(0)
            pw = pinentry.get_pin(description="Enter hashpass master password:",
                                  prompt="Password:",
                                  errormsg="That doesn't match the stored master.")
        use_master(pw, use_bcrypt)
    except pinentry.PinEntryException:
        return get_password_cli()

def send_to_clipboard(text):
    if subprocess.call(["which", "xclip"], stdout=open(os.devnull, 'wb')) == 0:
        cliptimesh = os.path.abspath(os.path.join(os.path.dirname(__file__), "cliptime.sh"))
        subprocess.call([cliptimesh, str(CLIP_SECONDS), text])
    else:
        import pyperclip
        pyperclip.copy(text)

def cli(arguments):
    """ runs the app with the CLI as the user interface """
    use_bcrypt = arguments['--bcrypt']

    init()
    get_password(use_bcrypt)
    if arguments['<website>']:
        w = arguments['<website>']
        result = make_password(w)
        if arguments['--show']:
            print result
        else:
            send_to_clipboard(result)
            print "The password is in your clipboard."
    else:
        while True:
            try:
                w = raw_input("Website name: ")
            except (KeyboardInterrupt, EOFError):
                print ""
                return
            if w == "":
                return
            result = make_password(w)
            if arguments['--show']:
                print result
            else:
                send_to_clipboard(result)
                print "The password is in your clipboard."

if __name__ == "__main__":
    cli(docopt(__doc__, version='HashPass 1.0'))
