#!/usr/bin/env python3.3

from remoteShell import remoteShell

import socket
import shlex
import subprocess

class remoteShellServer:
    """This is the remote shell server"""

    _host = None
    _port = None
    _sock = None
    _client = None

    def __init__(self, host, port):
        self._host = host
        self._port = port

        self.start()

    def start(self):

        try:
            self._sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        except socket.error as msg:
            print('Can not create socket')
            exit()
        else:
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self._sock.bind((self._host, self._port))
        except ConnectionRefusedError as e:
            print('Can not bind socket')
            exit()

        try:
            self._sock.listen(1)
        except ConnectionRefusedError as e:
            print('Can not listen')
            exit()
        else:
            self._client, address = self._sock.accept()
            self.loop()

    def loop(self):
        exit = False

        while not exit:
            cmd = self.recv()

            if cmd == remoteShell._EXIT:
                exit = True
                continue
            else:
                args = shlex.split(cmd)
                stdout, stderr = ("", "")

                try:
                    sub = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except OSError as e:
                    stderr = bytes("%s: command not found" % cmd, 'utf-8')
                else:
                    stdout, stderr= sub.communicate()

                self.send(stdout, stderr)

        self.quit()

    def recv(self):
        response = ""
        recv = True

        while recv == True:

            data = self._client.recv(remoteShell._BUFFER_SIZE).decode("utf-8")

            if data.find(remoteShell._END_FLAG) != -1:
                recv = False

            response = response+data

        begin = response.find(remoteShell._BEGIN_FLAG)
        end = response.find(remoteShell._END_FLAG)

        response = response[begin:end]
        response = response.replace(remoteShell._BEGIN_FLAG, "")

        return response

    def send(self, stdout, stderr):
        self._client.send(bytes(remoteShell._BEGIN_FLAG, "utf-8"))

        if stdout:
            self._client.send(stdout)

        if stderr:
            self._client.send(stderr)

        self._client.send(bytes(remoteShell._END_FLAG, "utf-8"))

    def quit(self):
        self._client.close()
        self._sock.close()
        exit()

if __name__ == '__main__':
    remoteShellServer("127.0.0.1", 3465)