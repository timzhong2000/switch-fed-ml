from packet import Packet
from typing import List
from multiprocessing import Process

from node import Node
import numpy as np
import threading


class Server(Node):

    def __init__(self, ip_addr: str, port: int, rpc_port: int, node_id: int, is_remote_node: bool):
        super().__init__(ip_addr, port, rpc_port, node_id, is_remote_node)

    def close(self):
        self._close()

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
