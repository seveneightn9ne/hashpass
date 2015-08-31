#!/usr/bin/env python
import os.path, hashlib, getpass, sys, pyperclip
from subprocess import Popen, PIPE

MASTER_PW_DIR = os.path.expanduser("~/.config/hashpass/")
MASTER_PW_FILE = "password.sha512"
MASTER_PW_PATH = MASTER_PW_DIR + MASTER_PW_FILE

LETTERS = "abcdefghjkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXY"
NUMBERS = "3456789"
SYMBOLS = "#*@()+={}?"

session_master = None

def get_hashed_master():
    """
    Gets the SHA512 of the master saved on disk at MASTER_PW_PATH.
    If that file doesn't exist, returns None.
    """
    return open(MASTER_PW_PATH, 'r').read() if os.path.exists(MASTER_PW_PATH) else None

def save_master(master_plaintext):
    """ Saves the SHA512 of master_plaintext to MASTER_PW_PATH. """
    os.makedirs(MASTER_PW_DIR)
    with os.fdopen(os.open(MASTER_PW_PATH, os.O_WRONLY | os.O_CREAT, 0600), 'w') as f:
        f.write(hashlib.sha512(master_plaintext).hexdigest())
    global session_master
    session_master = master_plaintext

def is_correct_master(password):
    """ Returns True if the password matches the stored master, else False. """
    global session_master
    if session_master:
        return session_master == password
    if get_hashed_master() == hashlib.sha512(password).hexdigest():
        session_master = password
        return True
    return False

def _to_chars(nums):
    """ Three 8-bit numbers map to a string of 4 password-safe characters """
    charset = LETTERS + NUMBERS + SYMBOLS
    if not len(charset) == 64:
        raise Exception("Bad charset wrong length")
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
        r.append(lst[size*i:size*i + size])
    return r

def hash(string):
    """ SHA256 hash the string and convert to the 64 character charset. """
    return reduce(lambda a,b: a+b,
            map(_to_chars, _chunks(map(ord, hashlib.sha256(string).digest()))))

def is_good_pass(password):
    """ If the password is 20 characters and inculdes a symbol, it is good. """
    return reduce(lambda a,b: a or b, [s in password for s in SYMBOLS])

def make_password(password, website):
    """
    Turns the password + website into a 20 character password.
    The password is_good_pass and is deterministic.
    """
    passwords = _chunks(hash(website+password), size=20)
    while True:
        for password in passwords:
            if is_good_pass(password):
                return password
        passwords = _chunks(hash("".join(passwords)), size=20)


def _test_to_chars():
    if not _to_chars([0, 0, 0]) == "aaaa":
        print "Failed test 1"
    if not _to_chars([255, 255, 255]) == "????":
        print "Failed test 2"
    if not _to_chars([4,32,196]) == "bcde":
        print "Failed test 3"

def _test_is_good_pass():
    if not is_good_pass("#"):
        print "Failed test 4"
    if is_good_pass(""):
        print "Failed test 5"
    if not is_good_pass("ooooo#oo"):
        print "Failed test 6"
    if is_good_pass("oeuoeuOOO2343"):
        print "Failed test 7"

def _test_make_password():
    if not make_password("a","b") == "P4{tRc6X3q}5)bCw}su=":
        print "Failed test 8"

def run_tests():
    """ Run all tests and print if there is a failure """
    _test_to_chars()
    _test_is_good_pass()
    _test_make_password()
