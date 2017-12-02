import threading
import socket
from queue import Queue

from node import Node

nodes = []

class NodeListener(threading.Thread):

    def __init__(self, server):
        threading.Thread.__init__(self, args=(), kwargs=None)
        self.server = server
        self.shutdown_flag = threading.Event()

    def run(self):
        while not self.shutdown_flag.is_set():
            client, addr = self.server.accept()
            nodes.append(Node(Queue(), client, addr))


class Server(threading.Thread):

    def __init__(self, commands, localaddr):
        threading.Thread.__init__(self, args=(), kwargs=None)

        self.localaddr = localaddr
        self.commands = commands
        self.shutdown_flag = threading.Event()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.localaddr)
        self.server.listen(10)

    def run(self):
        # start node listener thread
        node_listener = NodeListener(self.server)
        node_listener.start()
        while not self.shutdown_flag.is_set():
            cmd = self.commands.get()
            if cmd is None:
                break
            self.run_command(cmd)

        for node in nodes:
            node.shutdown_flag.set()
        self.server.close()

    def run_command(self, cmd):
        for node in nodes:
            with node.queue.mutex:
                node.queue.queue.clear()
            node.queue.put(cmd)