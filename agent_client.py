"""
Client for communicating with the agent.
"""
import sys
import os
import json
import socket
import traceback
import contextlib
import agent
import logging


# Set up logging.
logging.getLogger().disabled = True


class AgentClientException(Exception):
    pass


def is_alive():
    """Whether the agent is alive."""
    try:
        return ping() is not None
    except AgentClientException:
        return False


def ping():
    return _send_object({"type": "ping"})


def get_password(slug):
    """
    Ask the agent to make a password.

    Returns: password or None
    """
    res = _send_object({
        "type": "get_password",
        "slug": slug,
    })
    if "password" in res:
        return str(res["password"])
    else:
        return None


def send_shutdown():
    _send_object({"type": "shutdown"})


def _send_string(message):
    """Send and receive a string."""
    with contextlib.closing(socket.socket(
            socket.AF_UNIX,
            socket.SOCK_STREAM)) as sock:
        try:
            sock.connect(agent.daemon_sock_path())
        except socket.error as exc:
            raise AgentClientException("Could not connect.", exc)

        sock.settimeout(30)

        try:
            sock.sendall(message)
        except socket.error as exc:
            raise AgentClientException("Send failed.", exc)

        try:
            res = sock.recv(4096)
        except socket.timeout as exc:
            raise AgentClientException("Receive timed out.", exc)
        except socket.error as exc:
            raise AgentClientException("Receive failed.", exc)

        return res


def _send_object(message):
    """Send and receive and object as json."""
    res = _send_string(json.dumps(message))
    try:
        res = json.loads(res)
    except ValueError as exc:
        raise AgentClientException(
            "Received invalid json.", res, exc)
    return res


if __name__ == "__main__":
    print ping()
