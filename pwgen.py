#!/usr/bin/env python
import os.path, hashlib, getpass, sys
from subprocess import Popen, PIPE

MASTER_PW_DIR = os.path.expanduser("~/.config/pwgen/")
MASTER_PW_FILE = "password.sha512"
MASTER_PW_PATH = MASTER_PW_DIR + MASTER_PW_FILE
def init():
    if not os.path.exists(MASTER_PW_PATH):
        hashedpw = hashlib.sha512(
                getpass.getpass("No master password found. Enter one now: ").encode()).hexdigest()
        print "Your master password will be hashed and saved at " + MASTER_PW_PATH
        os.makedirs(MASTER_PW_DIR)
        with open(MASTER_PW_PATH, 'w') as f:
            f.write(hashedpw)

def get_password():
    correct_hash = open(MASTER_PW_PATH, 'r').read()
    pw = getpass.getpass("Enter master password: ")
    hashed_pw = hashlib.sha512(pw.encode()).hexdigest()
    while correct_hash != hashed_pw:
        print "That doesn't match the stored master."
        pw = getpass.getpass("Try again: ")
        hashed_pw = hashlib.sha512(pw.encode()).hexdigest()
    return pw

def send_to_clipboard(text):
    p = Popen('xclip -selection clipboard', stdin=PIPE)
    p.communicate(input=text)

if __name__ == "__main__":
    init()
    if (len(sys.argv) < 2):
        w = raw_input("Website name: ")
    else:
        w = sys.argv[1]
    p = get_password()
    result = hashlib.sha1((w+p).encode()).hexdigest()
    send_to_clipboard(result)
    print "The password is in your clipboard."


