#!/usr/bin/env python
from hashpasslib import *
import pinentry

import os.path, hashlib, getpass, sys, pyperclip
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
    """ Gets the password via pinentry if possible fallback to CLI. """
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
    pyperclip.copy(text)

def cli():
    """ runs the app with the CLI as the user interface """
    init()
    get_password()
    if len(sys.argv) >= 2:
        w = sys.argv[1]
        result = make_password(w)
        send_to_clipboard(result)
        print "The password is in your clipboard."
    else:
        while True:
            try:
                w = raw_input("Website name: ")
            except KeyboardInterrupt:
                return
            if w == "":
                return
            result = make_password(w)
            send_to_clipboard(result)
            print "The password is in your clipboard."

if __name__ == "__main__":
    cli()

