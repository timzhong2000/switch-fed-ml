from packet import *
from typing import List
import time
from node import Node
import numpy as np
import threading
from node import Node

class Server(Node):

    def __init__(self, ip_addr: str, rx_port: int, tx_port: int, rpc_port: int, node_id: int, is_remote_node: bool):
        super().__init__(ip_addr, rx_port, tx_port, rpc_port, node_id, is_remote_node)
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
        packet_list = self._create_packets(group_id, tensor_id, tensor) # TODO: 如果是 switch，添加 multicast

        send_start = time.time()
        server_addr = (node.options['ip_addr'], node.options['rx_port'])
        total_packet_num = len(packet_list)
        for i in range(total_packet_num):
            self.tx_sock.sendto(packet_list[i].buffer, server_addr)
            # TODO: 限速
            if i % 128 == 0:
                time.sleep(0.002)
        send_end = time.time()
        print("发送耗时 %f 发送速率 %f Mbps" % (
            send_end - send_start,
            elemenet_per_packet * total_packet_num * 4 / 1024 / 1024 * 8 / (send_end - send_start)))

        if node.type=="switch":
            for client in node.children.values():
                missing_slice = client.rpc_stub.ReadMissingSlice(tensor_id, self.options['node_id'])
                client.rpc_stub.Retransmission(tensor_id, self.options['node_id'], {})
        else:
            missing_slice = node.rpc_stub.ReadMissingSlice(tensor_id, self.options['node_id'])
            node.rpc_stub.Retransmission(tensor_id, self.options['node_id'], {})
        return

    def receive_thread(self) -> None:
        pkt = Packet()
        while True:
            _, client = self.rx_socket.recvfrom_into(pkt.buffer, pkt_size)
            pkt.parse_header()
            pkt.parse_payload()
            key: tuple = (pkt.tensor_id, pkt.node_id)
            job = self.rx_jobs.get(key)
            if job is None:
                continue
            job.handle_packet(pkt)
            self.rx_socket.sendto(pkt.gen_ack_packet(), client)

    def get_node_list_by_group_id(self, group_id: int):
        # TODO
        return self.children