#!/usr/bin/env python
import os.path, hashlib, getpass, sys, pyperclip
from subprocess import Popen, PIPE

MASTER_PW_DIR = os.path.expanduser("~/.config/hashpass/")
MASTER_PW_FILE = "password.sha512"
MASTER_PW_PATH = MASTER_PW_DIR + MASTER_PW_FILE
def init():
    """ Saves the master password to disk if you haven't already """
    if not os.path.exists(MASTER_PW_PATH):
        hashedpw = hashlib.sha512(
                getpass.getpass("No master password found. Enter one now: ").encode()).hexdigest()
        print "Your master password will be hashed and saved at " + MASTER_PW_PATH
        os.makedirs(MASTER_PW_DIR)
        with open(MASTER_PW_PATH, 'w') as f:
            f.write(hashedpw)

def get_password():
    """ Gets the password via CLI and makes sure it matches the stored password """
    correct_hash = open(MASTER_PW_PATH, 'r').read()
    pw = getpass.getpass("Enter master password: ")
    hashed_pw = hashlib.sha512(pw.encode()).hexdigest()
    while correct_hash != hashed_pw:
        print "That doesn't match the stored master."
        pw = getpass.getpass("Try again: ")
        hashed_pw = hashlib.sha512(pw.encode()).hexdigest()
    return pw

def send_to_clipboard(text):
    pyperclip.copy(text)

def _to_chars(nums):
    """ Three 8-bit numbers map to a string of 4 password-safe characters """
    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890#*"
    nums4 = ((nums[0] & 0xFC) >> 2,
            ((nums[0] & 0x3) << 4) | ((nums[1] & 0xF0) >> 4),
            ((nums[1] & 0x0F) << 2) | ((nums[2] & 0xC0) >>  6),
             nums[2] & 0x3F)
    #print map(lambda n: "{0:b}".format(n), nums)
    #print map(lambda n: "{0:b}".format(n), nums4)
    return reduce(lambda a,b: a+b, map(lambda i: charset[i], nums4))

def _chunks(lst, size=3):
    r = []
    for i in range(len(lst)/size):
        r.append(lst[3*i:3*i + 3])
    print r
    return r

def hash(password, website):
    """ Turn the password + website into a 20 character long password """
    return reduce(lambda a,b: a+b,
            map(_to_chars, _chunks(map(ord, hashlib.sha256(website + password).digest()))))[:20]

def cli():
    """ runs the app with the CLI as the user interface """
    init()
    w = raw_input("Website name: ") if len(sys.argv) < 2 else sys.argv[1]
    p = get_password()
    #result = hashlib.sha1((w+p).encode()).hexdigest()
    result = hash(p, w)
    send_to_clipboard(result)
    print "The password is in your clipboard."

def _test_to_chars():
    if not _to_chars([0, 0, 0]) == "aaaa":
        print "Failed test 1"
    if not _to_chars([255, 255, 255]) == "****":
        print "Failed test 2"
    if not _to_chars([4,32,196]) == "bcde":
        print "Failed test 3"

if __name__ == "__main__":
    cli()
    _test_to_chars()


