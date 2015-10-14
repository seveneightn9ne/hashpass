#!/usr/bin/env python
"""
Usage: hashpass [options] [<website>]

Options:
    -s --show    Display the password instead of putting it in the clipboard
    -b --bcrypt  Use bcrypt as the hashing algorithm [Recommended]
    --sha        Use sha256 as the hashing algorithm [Default]

"""
from hashpasslib import *
import pinentry

import os.path, hashlib, getpass, sys
from docopt import docopt
from subprocess import Popen, PIPE

def init():
    """ Saves the master password to disk if you haven't already """
    if not get_hashed_master():
        save_master(getpass.getpass("No master password found. Enter one now: "))
        print "Your master password will be hashed and saved at " + MASTER_PW_PATH

def get_password_cli():
    """ Gets the password via CLI and makes sure it matches the stored password """
    pw = getpass.getpass("Enter master password: ")
    while not is_correct_master(pw):
        print "That doesn't match the stored master."
        pw = getpass.getpass("Try again: ")
    # when is_correct_master(pw) it will be saved

def get_password():
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
    except pinentry.PinEntryException:
        return get_password_cli()

def send_to_clipboard(text):
    import pyperclip
    pyperclip.copy(text)

def cli(arguments):
    """ runs the app with the CLI as the user interface """
    init()
    get_password()
    if arguments['<website>']:
        w = arguments['<website>']
        result = make_password(w, arguments['--bcrypt'])
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
            result = make_password(w, arguments['--bcrypt'])
            if arguments['--show']:
                print result
            else:
                send_to_clipboard(result)
                print "The password is in your clipboard."

if __name__ == "__main__":
    cli(docopt(__doc__, version='HashPass 1.0'))

