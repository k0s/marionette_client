import json
import socket

class MarionetteClient(object):

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.sock = None
        self.traits = None
        self.applicationType = None

    def _recv_n_bytes(self, n):
        """ Convenience method for receiving exactly n bytes from
            self.sock (assuming it's open and connected).
        """
        data = ''
        while len(data) < n:
            chunk = self.sock.recv(n - len(data))
            if chunk == '':
                break
            data += chunk
        return data

    def receive(self):
        """ Receive the next complete response from the server, and return
            it as a dict.  Each response from the server is prepended by
            len(message) + ':'.
        """
        assert(self.sock)
        response = self.sock.recv(10)
        sep = response.find(':')
        length = response[0:sep]
        response = response[sep + 1:]
        response += self._recv_n_bytes(int(length) + 1 + len(length) - 10)
        return json.loads(response)

    def connect(self):
        """ Connect to the server and process the hello message we expect
            to receive in response.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.addr, self.port))
        hello = self.receive()
        self.traits = hello.get('traits')
        self.applicationType = hello.get('applicationType')

    def send(self, msg):
        """ Send a message on the socket, prepending it with len(msg) + ':'.
        """
        if not self.sock:
            self.connect()
        data = json.dumps(msg)
        self.sock.send('%s:%s' % (len(data), data))
        response = self.receive()
        return response

    def close(self):
        self.sock.close()
        self.sock = None
