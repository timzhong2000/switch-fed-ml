from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Null(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class PacketLoss(_message.Message):
    __slots__ = []
    class Request(_message.Message):
        __slots__ = ["node_id", "tensor_id"]
        NODE_ID_FIELD_NUMBER: _ClassVar[int]
        TENSOR_ID_FIELD_NUMBER: _ClassVar[int]
        node_id: int
        tensor_id: int
        def __init__(self, tensor_id: _Optional[int] = ..., node_id: _Optional[int] = ...) -> None: ...
    class Response(_message.Message):
        __slots__ = ["missing_packet_list"]
        MISSING_PACKET_LIST_FIELD_NUMBER: _ClassVar[int]
        missing_packet_list: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, missing_packet_list: _Optional[_Iterable[int]] = ...) -> None: ...
    def __init__(self) -> None: ...

class Retransmission(_message.Message):
    __slots__ = []
    class Request(_message.Message):
        __slots__ = ["data", "node_id", "tensor_id"]
        class DataEntry(_message.Message):
            __slots__ = ["key", "value"]
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: str
            def __init__(self, key: _Optional[int] = ..., value: _Optional[str] = ...) -> None: ...
        DATA_FIELD_NUMBER: _ClassVar[int]
        NODE_ID_FIELD_NUMBER: _ClassVar[int]
        TENSOR_ID_FIELD_NUMBER: _ClassVar[int]
        data: _containers.ScalarMap[int, str]
        node_id: int
        tensor_id: int
        def __init__(self, tensor_id: _Optional[int] = ..., node_id: _Optional[int] = ..., data: _Optional[_Mapping[int, str]] = ...) -> None: ...
    def __init__(self) -> None: ...

class Sync(_message.Message):
    __slots__ = []
    class SendBarrierRequest(_message.Message):
        __slots__ = ["node_id", "tensor_id"]
        NODE_ID_FIELD_NUMBER: _ClassVar[int]
        TENSOR_ID_FIELD_NUMBER: _ClassVar[int]
        node_id: int
        tensor_id: int
        def __init__(self, node_id: _Optional[int] = ..., tensor_id: _Optional[int] = ...) -> None: ...
    def __init__(self) -> None: ...
