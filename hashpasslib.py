#!/usr/bin/env python
import os.path
import alg

MASTER_PW_DIR = os.path.expanduser("~/.config/hashpass/")
MASTER_PW_FILE = "password.bcrypt"
MASTER_PW_PATH = MASTER_PW_DIR + MASTER_PW_FILE

session_master = None
session_intermediate = None

def use_master(master_plaintext, use_bcrypt=False):
    global session_master
    global session_intermediate
    session_master = master_plaintext
    if use_bcrypt:
        session_intermediate = alg.make_intermediate(session_master)
    else:
        session_intermediate = session_master

def read_stored_master():
    """
    Gets the stored component of the master saved on disk at MASTER_PW_PATH.
    If that file doesn't exist, returns None.
    """
    return open(MASTER_PW_PATH, 'r').read() if os.path.exists(MASTER_PW_PATH) else None

def store_master(master_plaintext):
    """Safely stores a derivation of the master to MASTER_PW_PATH for checking against."""
    os.makedirs(MASTER_PW_DIR)
    with os.fdopen(os.open(MASTER_PW_PATH, os.O_WRONLY | os.O_CREAT, 0600), 'w') as f:
        f.write(alg.make_storeable(master_plaintext))

def is_correct_master(password):
    """ Returns True if the password matches the stored master, else False. """
    global session_master
    if session_master:
        return session_master == password
    stored_component = read_stored_master()
    if (stored_component is not None
        and alg.check_stored(password, stored_component)):
        return True
    return False

def make_password(slug):
    """
    Turns the password + slug into a 20 character password.
    The password is_good_pass and is deterministic.
    """
    if not session_intermediate:
        raise Exception("Cannot make password without an intermediate pw.")
    return alg.make_site_password(session_intermediate, slug)
