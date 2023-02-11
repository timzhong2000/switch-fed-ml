from node import Node
import numpy as np
import math
from packet import *
import time 
import socket

class Client(Node):
    def __init__(self, ip_addr: str, rx_port: int, tx_port: int, rpc_port: int, node_id: int, is_remote_node: bool):
        super().__init__(ip_addr, rx_port, tx_port, rpc_port, node_id, is_remote_node)
        self.type = "client"

    # tensor 长度需要被 elemenet_per_packet 整除
    def send(self, server: Node, group_id: int, tensor_id: int, tensor: np.ndarray, has_switch: bool) -> int:
        server_addr = (server.options['ip_addr'], server.options['rx_port'])
        packet_list = self._create_packets(group_id, tensor_id, tensor, 0 if has_switch else bypass_bitmap)

        # 一次性发出发送窗口所有包
        finish_cnt = 0
        window_size = switch_pool_size # TODO: 对于互联网传输提供更大的 window
        send_window = []
        send_window_time = []
        total_packet_num = len(packet_list)
        for i in range(min(window_size, total_packet_num)):
            send_window.append(packet_list[i])
            send_window_time.append(time.time())
            self.tx_sock.sendto(send_window[i].buffer, server_addr)

        rtt = 0.001
        rx_pkt = Packet()
        send_start = time.time()

        while finish_cnt != total_packet_num:
            self.tx_sock.settimeout(rtt)
            try:
                self.tx_sock.recv_into(rx_pkt.buffer)
                rx_pkt.parse_header()
                if rx_pkt.ack and rx_pkt.tensor_id == send_window[rx_pkt.pool_id].tensor_id and rx_pkt.segment_id == send_window[rx_pkt.pool_id].segment_id:
                    finish_cnt += 1
                    next_packet_segment_id = send_window[rx_pkt.pool_id].segment_id + window_size
                    # 尝试发出这个窗口下一个包
                    if next_packet_segment_id < total_packet_num:
                        send_window[rx_pkt.pool_id] = packet_list[next_packet_segment_id]
                        send_window_time[rx_pkt.pool_id] = time.time()
                        self.tx_sock.sendto(
                            send_window[rx_pkt.pool_id].buffer, server_addr)
                if rx_pkt.ecn:
                    # TODO: 如果支持多任务，需要添加 ecn
                    pass
            except:
                # 找出超时的包重发
                now = time.time()
                for i in range(len(send_window)):
                    if now - send_window_time[i] > rtt:
                        send_window[i].flow_control |= retranmission_bitmap
                        send_window[i].deparse_header()
                        send_window_time[i] = now
                        try:
                            self.tx_sock.sendto(send_window[i].buffer, server_addr)
                        except:
                            pass
        send_end = time.time()
        print("发送耗时 %f 发送速率 %f Mbps" % (
            send_end - send_start,
            elemenet_per_packet * total_packet_num * 4 / 1024 / 1024 * 8 / (send_end - send_start)))
        
        server.rpc_retranmission(tensor_id, self.options['node_id'], {})
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
            # client 不需要 ack