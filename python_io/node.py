import numpy as np
import socket
import math
import packet
import time
import threading
from packet import Packet

elements_per_packet = 128


class Node:
    options = {
        "ip_addr": "",
        "port": 0,
        "rpc_port": 0,
        "node_id": 0
    }
    children = {}

    pending_tx_tensor = {}
    pending_tx_tensor_lock = threading.Lock()

    pending_rx_tensor_bitmap = {}
    pending_rx_tensor = {}
    pending_rx_tensor_lock = threading.Lock()

    def __init__(self, ip_addr: str, port: int, rpc_port: int, node_id: int):
        self.options['ip_addr'] = ip_addr
        self.options['port'] = port
        self.options['rpc_port'] = rpc_port
        self.options['node_id'] = node_id

    # tensor 长度需要被 128 整除
    def send(self, node, group_id: int, tensor_id: int, tensor: np.ndarray) -> int:
        self.pending_tx_tensor[tensor_id] = tensor
        total_packet_num = math.ceil(tensor.size / elements_per_packet)
        for i in range(total_packet_num):
            offset = i * 128
            pkt = Packet()
            pkt.set_header({
                "tensor_id": tensor_id,  # uint32
                "offset": offset,  # uint32
                "node_id": self.options['node_id'],  # uint16
                "aggregate_num": 1,         # uint16
                "ucast_grp": group_id,             # uint32
                "ecn": 0,                   # uint8
                "bypass": 0,                # uint8
                "data_type": packet.DataType.INT32.value  # uint8
            })
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
            self.pending_rx_tensor_lock.acquire()
            key: tuple = (pkt.header['tensor_id'], pkt.header['node_id'])
            tensor: np.ndarray = self.pending_rx_tensor.get(key)
            bitmap: np.ndarray = self.pending_rx_tensor_bitmap.get(key)
            if tensor is None or bitmap is None:
                continue
            tensor[pkt.header['offset']: pkt.header['offset'] + 128] = pkt.tensor
            bitmap[int(pkt.header['offset'] / 128)] = 1
            self.pending_rx_tensor_lock.release()
        return

    def receive(self, node, group_id: int, tensor_id: int, tensor: np.ndarray):
        total_packet_num = math.ceil(tensor.size / elements_per_packet)
        key: tuple = (tensor_id, node.options['node_id'])
        self.pending_rx_tensor[key] = tensor
        self.pending_rx_tensor_bitmap[key] = np.zeros(
            (total_packet_num), dtype=np.int8)
        # 固定传输时间，如果没有传输完成认为超时
        time.sleep(2)

        self.pending_rx_tensor_lock.acquire()
        tensor = self.pending_rx_tensor.pop(key)
        bitmap = self.pending_rx_tensor_bitmap.pop(key)
        self.pending_rx_tensor_lock.release()

        # TODO: 根据 bitmap 要求 node 重传丢包部分

        return

    def addChild(self, node):
        self.children[node.options.node_id] = node


# test
server = Node("127.0.0.1", 50000, 50001, 0)
client1 = Node('127.0.0.1', 50002, 50003, 1)
tensor0 = np.zeros((1024), dtype=np.int32)
tensor1 = np.ones((1024), dtype=np.int32)


def server_receive():
    server.receive(client1, 0, 12345, tensor0)
    return


def client_send():
    client1.send(server, 0, 12345, tensor1)


threading.Thread(target=server.receive_thread).start()

recv_thread1 = threading.Thread(target=server_receive)
recv_thread1.start()
send_thread = threading.Thread(target=client_send)
send_thread.start()

recv_thread1.join()
send_thread.join()
