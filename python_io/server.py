from packet import Packet
import math
from typing import List
from multiprocessing import Process

from node import Node
import numpy as np
import threading
import time
import socket


class Server(Node):
    def multicast(self, node_list: List[Node], group_id: int, tensor_id: int, tensor: np.ndarray):
        threads: List[threading.Thread] = []
        tensors: List[np.ndarray] = []

        for node in node_list:
            tensor_temp = np.zeros(tensor.shape, tensor.dtype)
            send_thread = threading.Thread(
                target=self.send,
                args=[node, group_id, tensor_id, tensor]
            )
            send_thread.start()
            tensors.append(tensor_temp)
            threads.append(send_thread)

        for thread in threads:
            thread.join()

    def reduce(self, node_list: List[Node], group_id: int, tensor_id: int, tensor: np.ndarray):
        threads: List[threading.Thread] = []
        tensors: List[np.ndarray] = []

        for node in node_list:
            tensor_temp = np.zeros(tensor.shape, tensor.dtype)
            receive_thread = threading.Thread(
                target=self.receive,
                args=[node, group_id, tensor_id, tensor_temp]
            )
            receive_thread.start()
            tensors.append(tensor_temp)
            threads.append(receive_thread)

        for thread in threads:
            thread.join()

        for recv_tensor in tensors:
            tensor += recv_tensor
        return

    def get_node_list_by_group_id(self, group_id: int):
        # TODO
        return self.children


if __name__ == '__main__':
    server = Server("127.0.0.1", 50000, 50001, 0)
    threading.Thread(target=server.receive_thread).start()

    # 256 * int32 = 1KB
    # 100MB
    tensor0 = np.zeros((100 * 1024 * 256), dtype=np.int32)
    tensor1 = np.ones((100 * 1024 * 256), dtype=np.int32)

    clients = []
    node_id = 1
    for i in range(6):
        client = Node('127.0.0.1', 50000+node_id*2, 50000+node_id*2+1, node_id)
        node_id += 1
        clients.append(client)

    for client in clients:
        Process(target=client.send, args=[server, 0, 12345, tensor1]).start()

    def server_receive():
        server.reduce(clients, 0, 12345, tensor0)
        print(tensor0)
        return

    receive_thread = threading.Thread(target=server_receive)
    receive_thread.start()
    receive_thread.join()
