from enum import Enum
import struct
import numpy as np
import typing


class DataType(Enum):
    INT32 = 0
    FLOAT32 = 1


# 包头结构
# flow_control  uint8
# tensor_id     uint32
# packet_num    uint32
# node_id       uint16
# aggregate_num uint16
# ucast_grp     uint32
# data_type     uint8
header_format = ">BIIHHIB"
header_size = struct.calcsize(header_format)

# packer param
elemenet_per_packet = 2048 # MTU 9000
# elemenet_per_packet = 256 # MTU 1100
switch_pool_size = 64
pkt_size = elemenet_per_packet * 4 + header_size


# flow control
# |  0  |  1  |   2    | 3 | 4 | 5 | 6 | 7 |
# | ack | ecn | bypass |   |   |   |   |   |
ack_bitmap = 1 << 0
ecn_bitmap = 1 << 1
bypass_bitmap = 1 << 2


class Packet:
    def __init__(self) -> None:
        self.buffer = bytearray(pkt_size)

        self.flow_control = 0
        self.tensor_id = 0
        self.packet_num = 0
        self.node_id = 0
        self.aggregate_num = 0
        self.ucast_grp = 0
        self.data_type = DataType.INT32.value

        # flow control
        self.ecn = 0
        self.ack = 0
        self.bypass = 0

        self.tensor: typing.Union[np.ndarray, None] = None

    def set_header(self, flow_control: int, tensor_id: int, packet_num: int, node_id: int, aggregate_num: int, ucast_grp: int, data_type: int):
        self.flow_control = flow_control
        self.tensor_id = tensor_id
        self.packet_num = packet_num
        self.node_id = node_id
        self.aggregate_num = aggregate_num
        self.ucast_grp = ucast_grp
        self.data_type = data_type
        self.ecn = flow_control & ecn_bitmap
        self.bypass = flow_control & bypass_bitmap
        self.ack = flow_control & ack_bitmap

    # 必须是 shape (elemenet_per_packet) 的 uint32
    def set_tensor(self, tensor: np.ndarray):
        self.tensor = tensor

    def parse_buffer(self):
        header_val = struct.unpack_from(header_format, self.buffer)
        self.set_header(
            header_val[0],
            header_val[1],
            header_val[2],
            header_val[3],
            header_val[4],
            header_val[5],
            header_val[6]
        )
        if self.ack or self.ecn:
            return
        self.set_tensor(np.frombuffer(
            self.buffer,
            dtype=np.uint32,
            offset=header_size
        ))
        return

    def deparse_buffer(self):
        self.buffer[0: header_size] = struct.pack(
            header_format,
            self.flow_control,
            self.tensor_id,
            self.packet_num,
            self.node_id,
            self.aggregate_num,
            self.ucast_grp,
            self.data_type
        )
        self.buffer[header_size: pkt_size] = self.tensor.tobytes()
        return

    def gen_ack_packet(self):
        return struct.pack(
            header_format,
            self.flow_control | ack_bitmap,
            self.tensor_id,
            self.packet_num,
            self.node_id,
            self.aggregate_num,
            self.ucast_grp,
            self.data_type
        )
