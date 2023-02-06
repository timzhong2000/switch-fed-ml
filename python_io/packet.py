from enum import Enum
import struct
import numpy as np
import typing


class DataType(Enum):
    INT32 = 0
    FLOAT32 = 1


# 包头结构
# flow_control  uint8
# data_type     uint8
# tensor_id     uint32
# segment_id    uint32
# node_id       uint16
# aggregate_num uint16
# ucast_grp     uint16
# pool_id       uint16

header_format = ">BBIIHHHH"
header_size = struct.calcsize(header_format)

# packer param
elemenet_per_packet = 2048  # MTU 9000
# elemenet_per_packet = 256 # MTU 1100
switch_pool_size = 4
pkt_size = elemenet_per_packet * 4 + header_size


# flow control
# |  0  |  1  |   2    |        3       | 4 | 5 | 6 | 7 |
# | ack | ecn | bypass | retransmission |   |   |   |   |
ack_bitmap = 1 << 0
ecn_bitmap = 1 << 1
bypass_bitmap = 1 << 2
retranmission_bitmap = 1 << 3


class Packet:
    def __init__(self) -> None:
        self.buffer = bytearray(pkt_size)

        self.flow_control = 0
        self.data_type = DataType.INT32.value
        self.tensor_id = 0
        self.segment_id = 0
        self.node_id = 0
        self.aggregate_num = 0
        self.ucast_grp = 0
        self.pool_id = 0

        # flow control
        self.ecn = 0
        self.ack = 0
        self.bypass = 0

        self.tensor: typing.Union[np.ndarray, None] = None

    def set_header(self, flow_control: int, data_type: int, tensor_id: int, segment_id: int, node_id: int, aggregate_num: int, ucast_grp: int, pool_id: int):
        self.flow_control = flow_control
        self.tensor_id = tensor_id
        self.segment_id = segment_id
        self.node_id = node_id
        self.aggregate_num = aggregate_num
        self.ucast_grp = ucast_grp
        self.data_type = data_type
        self.ecn = flow_control & ecn_bitmap
        self.bypass = flow_control & bypass_bitmap
        self.ack = flow_control & ack_bitmap
        self.pool_id = pool_id

    # 必须是 shape (elemenet_per_packet) 的 uint32
    def set_tensor(self, tensor: np.ndarray):
        self.tensor = tensor

    def parse_header(self):
        header_val = struct.unpack_from(header_format, self.buffer)
        self.set_header(
            header_val[0],
            header_val[1],
            header_val[2],
            header_val[3],
            header_val[4],
            header_val[5],
            header_val[6],
            header_val[7],
        )
        return

    # 从 buffer 中解析 payload
    def parse_payload(self):
        self.set_tensor(np.frombuffer(
            self.buffer,
            dtype=np.uint32,
            offset=header_size
        ))
        return

    # 将 header 写入 buffer
    def deparse_header(self):
        struct.pack_into(
            header_format,
            self.buffer,
            0,
            self.flow_control,
            self.data_type,
            self.tensor_id,
            self.segment_id,
            self.node_id,
            self.aggregate_num,
            self.ucast_grp,
            self.pool_id
        )
        return

    # 将 tensor 写入 buffer
    def deparse_payload(self):
        self.buffer[header_size: pkt_size] = self.tensor.tobytes()

    def gen_ack_packet(self):
        return struct.pack(
            header_format,
            self.flow_control | ack_bitmap,
            self.data_type,
            self.tensor_id,
            self.segment_id,
            self.node_id,
            self.aggregate_num,
            self.ucast_grp,
            self.pool_id,
        )
