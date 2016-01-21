import sys
import os
import time
import json
import socket
import math

if sys.version_info[0] != 2:
    raise "Must be using Python 2"

class SocketWriter(object):
    def __init__(self, path):
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.socket.connect(path)

    def send(self, payload):
        self.socket.send(json.dumps(payload) + "\n")

def daemon_dir_path():
    return os.path.abspath("/tmp/hashpass-{}.d".format(os.getuid()))

def daemon_pid_path():
    return os.path.join(daemon_dir_path(), "agent.pid")

def daemon_sock_path():
    return os.path.join(daemon_dir_path(), "agent.sock")

if __name__ == "__main__":
    socket_writer = SocketWriter(daemon_sock_path())
    print socket_writer.socket
    while True:
        time.sleep(1)
        x = math.sin(time.time() / 10.)
        y = x + 1
        payload = (x, y)
        print json.dumps(payload)
        socket_writer.send(payload)
