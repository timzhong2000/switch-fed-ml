from enum import Enum
import struct
import numpy as np


class DataType(Enum):
    INT32 = 0
    FLOAT32 = 1


# 包头结构
header_format = ">IIHHIBBB"


class Packet:
    def __init__(self) -> None:
        self.header = {
            "tensor_id": 0,             # uint32
            "offset": 0,                # uint32
            "node_id": 0,               # uint16
            "aggregate_num": 0,         # uint16
            "ucast_grp": 0,             # uint32
            "ecn": 0,                   # uint8
            "bypass": 0,                # uint8
            "data_type": DataType.INT32.value  # uint8
        }

    def set_header(self, tensor_id: int, offset: int, node_id: int, aggregate_num: int, ucast_grp: int, ecn: int, bypass: int, data_type: int):
        self.header = {
            "tensor_id": tensor_id,
            "offset": offset,
            "node_id": node_id,
            "aggregate_num": aggregate_num,
            "ucast_grp": ucast_grp,
            "ecn": ecn,
            "bypass": bypass,
            "data_type": data_type,
        }

    # 必须是 shape (128) 的 uint32
    def set_tensor(self, tensor: np.ndarray):
        self.tensor = tensor

    def from_buffer(self, buffer: str):
        header_val = struct.unpack_from(header_format, buffer)
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
        self.set_tensor(np.frombuffer(
            buffer,
            dtype=np.uint32,
            offset=struct.calcsize(header_format)
        ))
        return

    def to_buffer(self):
        header_buffer = struct.pack(
            header_format,
            self.header['tensor_id'],
            self.header['offset'],
            self.header['node_id'],
            self.header['aggregate_num'],
            self.header['ucast_grp'],
            self.header['ecn'],
            self.header['bypass'],
            self.header['data_type']
        )
        data_buffer = self.tensor.tobytes()
        return header_buffer + data_buffer
