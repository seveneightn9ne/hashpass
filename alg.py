"""
Hashpass algorithm components.

This module contains functions used to generate passwords.
Everything here is stateless.
"""

import bcrypt
import hashlib
import hmac


# Salt for generating intermediate. (13 rounds)
# REUSED_BCRYPT_SALT = bcrypt.gensalt(rounds=13)
REUSED_BCRYPT_SALT = "$2b$13$X5A4.IjQghzyTGwc0wgRre"
# Rounds to use for storage.
STORE_BCRYPT_ROUNDS = 13

LETTERS = "abcdefghjkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXY"
NUMBERS = "3456789"
SYMBOLS = "#*@()+={}?"


def make_intermediate(secret_master):
    """Generate a deterministic derived key from the master.

    Use bcrypt and a REUSED SALT to derive an intermediate.
    Note the this salt is the same for all of hashpass.
    This intermediate should be kept as secret as the master.

    Returns:
        An intermediate which is a bcrypt output string.
        Keep it secret, keep it safe, don't leave memory.
    """
    return bcrypt.hashpw(secret_master, REUSED_BCRYPT_SALT)

def make_site_password(secret_intermediate, slug, old):
    """Generate a site password from the secret_intermediate and site name.

    Args:
        secret_intermediate: The secret component derived from the master.
        slug: The site name.

    Returns:
        The password for the site, which is:
        - 20 characters
        - is_good_pass
        - deterministic
    """
    if old:
        return make_site_password_old(secret_intermediate, slug)
    else:
        return make_site_password_new(secret_intermediate, slug)

def make_site_password_new(secret_intermediate, slug):
    """
    1. Concatenate (slug, generation, counter) separated by newlines.
    2. Hash (HMAC-Sha256) with secret_intermediate as the key.
    3. Truncate and convert to output character set.
    4. Try again with counter++ if candidate does not satisfy constraints.
    """
    limit = 10000
    generation = 0 # can be used for future features.
    for counter in xrange(limit):
        combined = "\n".join((slug, str(generation), str(counter)))
        hashed_string = _new_hash(secret_intermediate, combined)
        hashed_bytes = map(ord, hashed_string)
        assert len(hashed_bytes) == 32
        candidate = _bytes_to_password_candidate(hashed_bytes[:15])
        if is_good_pass(candidate):
            return candidate

    print "Could not find password after {} tries.".format(limit)
    print "This is improbable or something is wrong."
    raise Exception("Password reroll limit reached")

def make_site_password_old(secret_intermediate, slug):
    """
    1. Concatenate secret_intermediate with slug.
    2. Hash (SHA256) to produce two candidates.
    3. Convert to output character set.
    4. Re-roll if candidates do not satisfy constraints.
    """

    limit = 10000
    reroll_count = 0

    hashed_string = _old_hash(secret_intermediate, slug)

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
            hashed_string = _old_hash("", "".join(candidates))

    print "Could not find password after {} tries.".format(limit)
    print "This is improbable or something is wrong."
    raise Exception("Password reroll limit reached")

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

def make_storeable(secret_master):
    """Create something that can be safely stored to verify a master.

    Bcrypt the master with a RANDOM salt.

    Returns:
        A bcrypted string.
    """
    return bcrypt.hashpw(secret_master, bcrypt.gensalt(rounds=STORE_BCRYPT_ROUNDS))

def check_stored(secret_master, stored_component):
    """Check a master against a stored component.

    Returns:
        A bool of whether it is a match.
    """
    unverified_hash = bcrypt.hashpw(secret_master, stored_component)
    return unverified_hash == stored_component

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

def _old_hash(secret, data):
    combined = "{}{}".format(data, secret)
    return hashlib.sha256(combined).digest()

def _new_hash(secret, data):
    return hmac.new(key=secret, msg=data, digestmod=hashlib.sha256).digest()
