import numpy as np
import socket
import math
import packet
import time
import threading
from packet import Packet

elements_per_packet = 128


class Node:
    def __init__(self, ip_addr: str, port: int, rpc_port: int, node_id: int):
        self.options = {
            "ip_addr": ip_addr,
            "port": port,
            "rpc_port": rpc_port,
            "node_id": node_id,
            "groups": [0]
        }
        self.children = {}

        self.pending_tx_tensor: dict[int, np.ndarray] = {}
        self.pending_tx_tensor_lock = threading.Lock()

        self.pending_rx_tensor_bitmap: dict[(int, int), np.ndarray] = {}
        self.pending_rx_tensor: dict[(int, int), np.ndarray] = {}
        self.pending_rx_tensor_lock = threading.Lock()

    # tensor 长度需要被 128 整除
    def send(self, node, group_id: int, tensor_id: int, tensor: np.ndarray) -> int:
        self.pending_tx_tensor[tensor_id] = tensor
        total_packet_num = math.ceil(tensor.size / elements_per_packet)

        for i in range(total_packet_num):
            offset = i * 128
            pkt = Packet()
            pkt.set_header(
                tensor_id=tensor_id,  # uint32
                offset=offset,  # uint32
                node_id=self.options['node_id'],  # uint16
                aggregate_num=1,         # uint16
                ucast_grp=group_id,             # uint32
                ecn=0,                   # uint8
                bypass=0,                # uint8
                data_type=packet.DataType.INT32.value  # uint8
            )
            pkt.set_tensor(tensor[offset: offset+128])
            self.send_by_udp(node, group_id, pkt)

        # TODO: 等待对方完成接收（如果 node 是 switch 则等待 switch 下面所有节点接收完成）

        del self.pending_tx_tensor[tensor_id]
        return

    def send_by_udp(self, node, group_id: int, packet: Packet) -> int:
        dst_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dst_socket.sendto(packet.to_buffer(),
                          (node.options['ip_addr'], node.options['port']))
        return

    def receive_thread(self) -> None:
        bind_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bind_socket.bind((self.options['ip_addr'], self.options['port']))
        while True:
            buffer, client = bind_socket.recvfrom(1500)
            pkt = Packet()
            pkt.from_buffer(buffer)
            key: tuple = (pkt.header['tensor_id'], pkt.header['node_id'])
            tensor: np.ndarray = self.pending_rx_tensor.get(key)
            bitmap: np.ndarray = self.pending_rx_tensor_bitmap.get(key)
            if tensor is not None and bitmap is not None:
                tensor[pkt.header['offset']
                    : pkt.header['offset'] + 128] = pkt.tensor
                bitmap[int(pkt.header['offset'] / 128)] = 1

    # return packet received bitmap
    def receive(self, node, group_id: int, tensor_id: int, tensor: np.ndarray) -> np.ndarray:
        total_packet_num = math.ceil(tensor.size / elements_per_packet)
        key: tuple = (tensor_id, node.options['node_id'])
        self.pending_rx_tensor[key] = tensor
        self.pending_rx_tensor_bitmap[key] = np.zeros(
            (total_packet_num), dtype=np.int8)

        # TODO: 固定传输时间，如果没有传输完成认为超时
        # 预计传输时间可以用 rtt + 历史带宽 + 丢包率 计算
        time.sleep(2)

        self.pending_rx_tensor.pop(key)
        bitmap = self.pending_rx_tensor_bitmap.pop(key)
        print(bitmap.sum())

        # TODO: 根据 bitmap 要求 node 重传丢包部分

        return bitmap

    def addChild(self, node):
        self.children[node.options.node_id] = node
