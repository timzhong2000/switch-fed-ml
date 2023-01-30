from enum import Enum
import struct
import numpy as np


class DataType(Enum):
    INT32 = 0
    FLOAT32 = 1


# 包头结构
header_format = ">IIHHIBBB"


class Packet:
    header = {
        "tensor_id": 0,             # uint32
        "offset": 0,                # uint32
        "node_id": 0,               # uint16
        "aggregate_num": 0,         # uint16
        "ucast_grp": 0,             # uint32
        "ecn": 0,                   # uint8
        "bypass": 0,                # uint8
        "data_type": DataType.INT32.value  # uint8
    }

    def set_header(self, header: dict):
        self.header = header

    # 必须是 shape (128) 的 uint32
    def set_tensor(self, tensor: np.ndarray):
        self.tensor = tensor.astype(dtype=np.uint32)

    def from_buffer(self, buffer: str):
        header_val = struct.unpack_from(header_format, buffer)
        self.set_header({
            "tensor_id": header_val[0],
            "offset": header_val[1],
            "node_id": header_val[2],
            "aggregate_num": header_val[3],
            "ucast_grp": header_val[4],
            "ecn": header_val[5],
            "bypass": header_val[6],
            "data_type": header_val[7],
        })
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
