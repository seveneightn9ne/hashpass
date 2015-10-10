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

def _chunks(lst, size):
    """Divide a list into chunks of a certain size."""
    assert len(lst) % size == 0
    for i in xrange(0, len(lst), size):
        yield lst[i:i+size]

def _bytes_to_pw_chars(bytez):
    """Convert 3 bytes into 4 password characters.

    A password character is one in the set of:
    - letters
    - numbers
    - symbols

    Args:
        bytez: A list of 3 bytes.
    Returns:
        A string of 4 characters.
    """

    assert len(bytez) == 3
    # Make sure they're all bytes.
    assert all([x == x & 0xFF for x in bytez])

    charset = LETTERS + NUMBERS + SYMBOLS
    assert len(charset) == 64

    # Use 6-bit segments of the 24 bits from the 3 bytes
    # to select 4 characters from the size 64 charset.
            # Six high bytes from byte0
    nums4 = [(bytez[0] & 0xFC) >> 2,
            # 2 low bits of byte0, 4 high bits of byte1
            ((bytez[0] & 0x03) << 4) | ((bytez[1] & 0xF0) >> 4),
            # 4 low bits of byte1, 2 high bits of byte2
            ((bytez[1] & 0x0F) << 2) | ((bytez[2] & 0xC0) >>  6),
            # 6 low bits of byte2
            bytez[2] & 0x3F]
    chars4 = [charset[i] for i in nums4]
    return "".join(chars4)

def _bytes_to_password_candidate(bytez):
    """Convert 15 bytes into a password candidate.

    Args:
        bytez: A list of 15 byte values.

    Returns:
        A string of 20 characters.
    """
    assert len(bytez) == 15
    byte_tuples = list(_chunks(bytez, 3))
    assert len(byte_tuples) == 5
    char_tuples = map(_bytes_to_pw_chars, byte_tuples)
    assert len(byte_tuples) == 5
    converted = "".join(char_tuples)
    assert len(converted) == 20
    return converted

def is_good_pass(password):
    """Validate a password candidate.

    Must satisfy these rules:
    - exactly 20 characters
    - contains a letter
    - contains a number
    - contains a symbol
    """
    if len(password) != 20:
        return False
    return all([any([c in password for c in charset])
                for charset in (LETTERS, NUMBERS, SYMBOLS)])

def make_password(website):
    """
    Turns the password + website into a 20 character password.
    The password is_good_pass and is deterministic.
    """
    if not session_master:
        raise Exception("Cannot make password without a master pw")
    return make_password_inner(session_master, website)

def make_password_inner(master, website):
    """Generate a site password from the master and site name.

    1. Concatenate master onto website.
    2. Hash (SHA256) to produce two candidates.
    3. Convert to output character set.
    4. Re-roll if candidates do not satisfy constraints.

    Args:
        master: The plaintext master password.
        website: The site name.

    Returns: The password for that site.
    """
    limit = 10000
    reroll_count = 0
    combined = "{}{}".format(website, master)
    hashed_string = hashlib.sha256(combined).digest()
    for _ in xrange(limit):
        hashed_bytes = map(ord, hashed_string)
        assert len(hashed_bytes) == 32
        candidates = map(_bytes_to_password_candidate,
                         [hashed_bytes[:15], hashed_bytes[15:30]])
        if is_good_pass(candidates[0]):
            return candidates[0]
        elif is_good_pass(candidates[1]):
            reroll_count += 1
            return candidates[1]
        else:
            reroll_count += 2
            # Repeatedly hash to re-roll.
            # This rehash throws out the last 2 bytes each round.
            hashed_string = hashlib.sha256("".join(candidates)).digest()

    print "Could not find password after {} tries.".format(limit)
    print "This is improbable or something is wrong."
    raise Exception("Password reroll limit reached")
