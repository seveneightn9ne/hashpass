#!/usr/bin/env python
"""
Hashpass daemon like ssh-agent.
"""

import sys
import os
import os.path
import errno
import socket
import time
import datetime
import json
import contextlib
import logging
import fasteners
import daemon

import pinentry
import hashpasslib

# Set up logging.
logging.basicConfig(filename="./agent.log", level=logging.DEBUG)
logging.getLogger().disabled = True


# Credential lifetime in seconds.
CREDENTIALS_LIFETIME = datetime.timedelta(hours=12).total_seconds()


class AgentLockException(Exception):
    pass


def log_exception(exc_type, exc_value, exc_traceback):
    logging.critical("Uncaught exception.", exc_info=(exc_type, exc_value, exc_traceback))
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = log_exception


def daemon_dir_path():
    return os.path.abspath("/tmp/hashpass-{}.d".format(os.getuid()))


def daemon_lock_path():
    return os.path.join(daemon_dir_path(), "agent.lock")


def daemon_sock_path():
    return os.path.join(daemon_dir_path(), "agent.sock")


def create_daemon_dir():
    path = daemon_dir_path()

    try:
        os.mkdir(path, 0700)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

    os.chmod(path, 0700)


def getLogFileHandles(logger):
    """Get a list of filehandle numbers from logger to
    be handed to DaemonContext.files_preserve
    https://stackoverflow.com/questions/13180720/maintaining-logging-and-or-stdout-stderr-in-python-daemon
    """
    handles = []
    for handler in logger.handlers:
        handles.append(handler.stream.fileno())
    if logger.parent:
        handles += getLogFileHandles(logger.parent)
    return handles


@contextlib.contextmanager
def ipc_lock_nonblock(lock):
    """
    Contextmanager for using a fasteners ipc lock
    in a non-blocking way.
    """
    acquired = lock.acquire(blocking=False)
    if acquired:
        yield lock
        lock.release()
    else:
        raise AgentLockException("Could not acquire lock.")


def make_server_socket(path):
    """Create socket to listen on."""
    # Remove old socket.
    if os.path.exists(path):
        os.remove(path)

    # Set umask to create the socket with minimal permissions.
    old_umask = os.umask(0077)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(path)
    os.umask(old_umask)
    sock.listen(5)
    return sock


class _Agent(object):
    def __init__(self):
        self.canceled = False
        self.last_auth = time.time()

        self._run()

    def _run(self):
        logging.info("Agent started.")

        server_sock = make_server_socket(daemon_sock_path())
        self.canceled = False

        while not self.canceled:
            sock, addr = server_sock.accept()
            logging.debug("Connection from '{}'".format(addr))
            req = sock.recv(4096)
            logging.debug("Received: {}".format(req))
            try:
                req = json.loads(req)
            except ValueError as exc:
                logging.debug("Received invalid json.")
                continue
            res = self.process_message(req)
            if res == None:
                sock.close()
                continue
            res = json.dumps(res)
            try:
                sock.sendall(res)
            except socket.error as exc:
                if (isinstance(exc.args, tuple) and
                    exc.args[0] == errno.EPIPE):
                    logging.warn("Client left before being sent response.")
                else:
                    raise
            sock.close()

        logging.info("Shutting down by request.")
        sys.exit(0)

    def process_message(self, message):
        """Process a json message.

        This does user interaction and could block for a long time.

        Returns: Response to return to client.
        """
        if not isinstance(message, dict):
            return None
        mtype = message.get("type", None)

        self.maybe_expire_credentials()

        if mtype == None:
            return None

        if mtype == "ping":
            return {"pong": "pong"}
        if mtype == "get_password":
            slug = message.get("slug", None)
            if slug == None:
                return None

            # Try once to get a master.
            if not hashpasslib.is_ready():
                get_master_gui(use_bcrypt=True)
                if hashpasslib.is_ready():
                    self.last_auth = time.time()
            if hashpasslib.is_ready():
                password = hashpasslib.make_password(slug, old=False)
                return {"password": password}
            else:
                return {"error": "no master"}
        if mtype == "shutdown":
            self.canceled = True
            return {"ok": "ok"}

        # Unrecognized message type.
        return None

    def maybe_expire_credentials(self):
        """Expire credentials if it has been too long."""
        time_since_last_auth = time.time() - self.last_auth
        logging.debug("Time since last auth {}.".format(time_since_last_auth))
        if time_since_last_auth > CREDENTIALS_LIFETIME:
            logging.info("Expiring credentials.")
            hashpasslib.forget_master()


def get_master_gui(use_bcrypt):
    """Gets the password via pinentry.

    Calls use_master if it works, otherwise does nothing.

    Returns: None
    """
    try:
        pw = pinentry.get_pin(description="Enter hashpass master password:",
                              prompt="Password:")
        while pw is None or not hashpasslib.is_correct_master(pw):
            if pw == None:
                logging.warn("User canceled password entry.")
                return None
            pw = pinentry.get_pin(description="Enter hashpass master password:",
                                  prompt="Password:",
                                  errormsg="That doesn't match the stored master.")
        hashpasslib.use_master(pw, use_bcrypt)
    except pinentry.PinEntryException:
        logging.critical("Cannot use pinentry.")
        sys.exit(-1)
        return None


if __name__ == "__main__":
    print "Starting daemon."
    logging.info("Started launcher.")
    logging.debug("Creating daemon dir.")
    create_daemon_dir()

    # A inter-process lock to ensure only one agent runs per user.
    process_lock = fasteners.InterProcessLock(daemon_lock_path())

    # Disable initgroups because it requires root.
    with daemon.DaemonContext(
            files_preserve=getLogFileHandles(logging.getLogger()),
            initgroups=False):
        try:
            # Acquire the lock inside the daemon so the fd stays open.
            with ipc_lock_nonblock(process_lock):
                a = _Agent()

        except AgentLockException:
            logging.info("Aborting, could not acquire lock.")
            sys.exit(-1)

    logging.info("Shutting down.")
