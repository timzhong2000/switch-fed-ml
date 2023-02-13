from packet import *
from typing import List
import time
from node import Node
import numpy as np
import threading
from node import Node


class Server(Node):

    def __init__(self, ip_addr: str, rx_port: int, tx_port: int, rpc_port: int, node_id: int, is_remote_node: bool, iface: str = ""):
        super().__init__(ip_addr, rx_port, tx_port, rpc_port, node_id, is_remote_node, iface)
        self.type = "server"

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

    # 下发不检测丢包
    def send(self, node: Node, group_id: int, tensor_id: int, tensor: np.ndarray):
        packet_list = self._create_packets(
            group_id, tensor_id, tensor, multicast_bitmap if node.type == "switch" else bypass_bitmap)
        send_start = time.time()
        server_addr = (node.options['ip_addr'], node.options['rx_port'])
        total_packet_num = len(packet_list)
        for i in range(total_packet_num):
            self.tx_sock.sendto(packet_list[i].buffer, server_addr)
            # TODO: 限速
            if i % 128 == 0:
                time.sleep(0.001)
        send_end = time.time()
        print("发送耗时 %f 发送速率 %f Mbps" % (
            send_end - send_start,
            elemenet_per_packet * total_packet_num * 4 / 1024 / 1024 * 8 / (send_end - send_start)))

        if node.type == "switch":
            for client in node.children.values():
                self.check_and_retransmit(client, tensor_id, packet_list)
        else:
            self.check_and_retransmit(node, tensor_id, packet_list)
        return

    def receive_thread(self) -> None:
        pkt = Packet()
        while True:
            _, client = self.rx_sock.recvfrom_into(pkt.buffer, pkt_size)
            pkt.parse_header()
            pkt.parse_payload()
            key: tuple = (pkt.tensor_id, pkt.node_id)
            job = self.rx_jobs.get(key)
            if job is None:
                continue
            job.handle_packet(pkt)
            self.rx_sock.sendto(pkt.gen_ack_packet(), client)

    def get_node_list_by_group_id(self, group_id: int):
        # TODO
        return self.children
