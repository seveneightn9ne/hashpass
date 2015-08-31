#!/usr/bin/env python
from hashpasslib import *

import os.path, hashlib, getpass, sys, pyperclip
from subprocess import Popen, PIPE

def init():
    """ Saves the master password to disk if you haven't already """
    if not get_hashed_master():
        save_master(getpass.getpass("No master password found. Enter one now: "))
        print "Your master password will be hashed and saved at " + MASTER_PW_PATH

def get_password():
    """ Gets the password via CLI and makes sure it matches the stored password """
    pw = getpass.getpass("Enter master password: ")
    while not is_correct_master(pw):
        print "That doesn't match the stored master."
        pw = getpass.getpass("Try again: ")
    return pw

def send_to_clipboard(text):
    pyperclip.copy(text)

def cli():
    """ runs the app with the CLI as the user interface """
    init()
    w = raw_input("Website name: ") if len(sys.argv) < 2 else sys.argv[1]
    p = get_password()
    #result = hashlib.sha1((w+p).encode()).hexdigest()
    result = hash(p, w)
    send_to_clipboard(result)
    print "The password is in your clipboard."
if __name__ == "__main__":
    cli()
    _test_to_chars()


