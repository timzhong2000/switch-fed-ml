import numpy as np
import socket
import math
import threading
from packet import *
from job import Job
import grpc
from io_pb2_grpc import *
from io_pb2 import *
import typing
from grpc_server import GrpcServer
import time

add_delay_ms = 10


class Node:
    def __init__(self, ip_addr: str, rx_port: int, tx_port: int, rpc_port: int, node_id: int, is_remote_node: bool, iface: str, group_id: int = 10):
        self.options = {
            "ip_addr": ip_addr,
            "rx_port": rx_port,
            "tx_port": tx_port,
            "rpc_port": rpc_port,
            "node_id": node_id,
            "group": group_id,  # 所在的分组
            "speed": 100,  # 100 Mbps
        }
        self.type = "node"
        self.children: dict[int, Node] = {}
        self.iface = iface

        self.rx_jobs: dict[(int, int), Job] = {}
        self.rx_jobs_lock = threading.Lock()

        self.rpc_stub: typing.Optional[SwitchmlIOStub] = None
        self.rpc_server: typing.Optional[GrpcServer] = None
        self.rx_sock: typing.Optional[socket.socket] = None
        self.tx_sock: typing.Optional[socket.socket] = None

        if not is_remote_node:
            self.rx_sock = self._create_udp_socket()
            self.rx_sock.bind(
                (self.options['ip_addr'], self.options['rx_port']))
            self.tx_sock = self._create_udp_socket()
            self.tx_sock.bind((self.options['ip_addr'], self.options['tx_port']))
            print("成功监听数据端口 %s:%d" %
                  (self.options['ip_addr'], self.options['rx_port']))
            self.__receive_thread = threading.Thread(
                target=self.receive_thread)
            self.__receive_thread.start()
            print("成功启动接收线程 id=%d" % (self.__receive_thread.ident))
            self.rpc_server: GrpcServer = GrpcServer(self)
            print("成功启动 grpc 服务 %s:%d" %
                  (self.options['ip_addr'], self.options['rpc_port']))
        else:
            self._init_as_remote_node()

    def _create_udp_socket(self) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, self.iface.encode())
        return sock

    # stop the server
    def _close(self):
        print("grpc 服务正在关闭")
        self.rpc_server.stop()
        if self.tx_sock is not None:
            self.tx_sock.close()
        if self.rx_sock is not None:
            self.rx_sock.close()

    def _init_as_remote_node(self):
        addr = "%s:%d" % (self.options['ip_addr'], self.options['rpc_port'])
        channel = grpc.insecure_channel(addr)
        self.rpc_stub = SwitchmlIOStub(channel)

    def receive_async(self, node, tensor_id, tensor):
        # type: (Node, int, np.ndarray) -> Job
        key: tuple = (tensor_id, node.options['node_id'])
        job = Job(key, tensor)
        self.rx_jobs[key] = job
        return job

    def receive(self, node, tensor_id, tensor):
        # type: (Node, int, np.ndarray) -> None
        job = self.receive_async(node, tensor_id, tensor)
        job.wait_until_job_finish()

        received = job.bitmap.sum()
        total = job.bitmap.size
        print("receive %d packet, expect %d, loss %f %%" %
              (received, total, 100 * (total - received) / total))
        key: tuple = (tensor_id, node.options['node_id'])
        del self.rx_jobs[key]
        return

    def _create_packets(self, mcast_grp: int, tensor_id: int, tensor: np.ndarray, flow_control: int = 0) -> list:
        prepare_packet_start = time.time()
        total_packet_num = math.ceil(tensor.size / elemenet_per_packet)
        packet_list = []
        current_node_id = self.options['node_id']
        for i in range(total_packet_num):
            pkt = Packet()
            offset = i * elemenet_per_packet
            pkt.set_header(
                flow_control=flow_control,
                data_type=DataType.FLOAT32.value,  # uint8
                tensor_id=tensor_id,  # uint32
                segment_id=i,  # uint32
                node_id=current_node_id,  # uint16
                aggregate_num=1,         # uint16
                mcast_grp=mcast_grp,             # uint32
                pool_id=i % switch_pool_size
            )
            pkt.set_tensor(tensor[offset: offset+elemenet_per_packet])
            pkt.deparse_header()
            pkt.deparse_payload()
            packet_list.append(pkt)
        prepare_packet_end = time.time()

        print("构建包耗时 %f 构建速率 %f Mbps" % (
            prepare_packet_end - prepare_packet_start,
            tensor.size * 4 / 1024 / 1024 * 8 / (prepare_packet_end - prepare_packet_start)))
        return packet_list

    def add_child(self, node):
        # type: (Node) -> None
        self.children[node.options['node_id']] = node

    def remove_child(self, node) -> bool:
        # type: (Node) -> bool
        if self.children.get(node.options["node_id"]) is None:
            return False
        del self.children[node.options["node_id"]]
        return True

    # 向这个节点重传数据
    # 将会触发接收任务结束
    def rpc_retranmission(self, tensor_id, node_id, data):
        # type: (int, int, dict[int,  str]) -> None
        self.rpc_stub.Retransmission(
            Retransmission.Request(
                tensor_id=tensor_id,
                node_id=node_id,
                data=data
            )
        )

    # 获取这个节点的丢包状态
    def rpc_read_missing_slice(self, tensor_id, node_id):
        # type: (int, int) -> list
        return self.rpc_stub.ReadMissingSlice(
            PacketLoss.Request(
                tensor_id=tensor_id,
                node_id=node_id
            )
        )

    def check_and_retransmit(self, node, tensor_id, packet_list):
        #type: (Node, int, list)->int
        retransmit_start = time.time()
        missing_slice = node.rpc_stub.ReadMissingSlice(PacketLoss.Request(
            tensor_id=tensor_id, node_id=self.options['node_id'])).missing_packet_list
        payload = []
        for segment_id in missing_slice:
            payload.append(bytes(packet_list[segment_id].buffer))
        node.rpc_stub.Retransmission(Retransmission.Request(
            tensor_id=tensor_id, node_id=self.options['node_id'], data=payload))
        retransmit_end = time.time()
        return retransmit_end - retransmit_start