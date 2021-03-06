#!/usr/bin/env python3.3

from remoteShell import remoteShell

import socket

class remoteShellClient:
    """This is the remote shell client"""

    _host = None
    _port = None
    _sock = None

    def __init__(self, host, port):
        self._host = host
        self._port = port

        self.start()

    def start(self):
        self._sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        try:
            self._sock.connect((self._host, self._port))
        except ConnectionRefusedError as e:
            print('Connection refused')
            exit()
        else:
            self.loop()

    def loop(self):
        exit = False

        while not exit:
            cmd = self.input()

            if cmd == remoteShell._EXIT:
                exit = True
                self.send(cmd)
                continue
            else:
                self.send(cmd)
                print(self.recv())

        self.quit()

    def input(self):
        cmd = ""

        while cmd == "":
            try:
                cmd = input('>> ')
            except (KeyboardInterrupt, SystemExit):
                print("\n Enter '%s' to quit." % remoteShell._EXIT)

        return cmd

    def recv(self):
        response = ""
        recv = True

        while recv == True:

            data = self._sock.recv(remoteShell._BUFFER_SIZE).decode("utf-8")

            if data.find(remoteShell._END_FLAG) != -1:
                recv = False

            response = response+data

        begin = response.find(remoteShell._BEGIN_FLAG)
        end = response.find(remoteShell._END_FLAG)

        response = response[begin:end]
        response = response.replace(remoteShell._BEGIN_FLAG, "")

        return response

    def send(self, cmd):
        self._sock.send(bytes(remoteShell._BEGIN_FLAG, "utf-8"))
        self._sock.send(bytes(cmd, "utf-8"))
        self._sock.send(bytes(remoteShell._END_FLAG, "utf-8"))

    def quit(self):
        self._sock.close()
        exit()



if __name__ == '__main__':
    remoteShellClient("127.0.0.1", 3465)