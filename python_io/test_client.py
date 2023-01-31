from server import Server
from client import Client
import numpy as np

import time
from io_pb2_grpc import *
from io_pb2 import *

if __name__ == "__main__":
    tensor = np.ones((500 * 1024 * 256), dtype=np.int32)

    node_id = 1
    server = Server("127.0.0.1", 50000, 50001, 0, True)
    client = Client('127.0.0.1', 50000+node_id*2,
                    50000+node_id*2+1, node_id, False)
    start = time.time()
    client.send(server, 0, 12345, tensor)
    end = time.time()
    print(end-start)
    # channel = grpc.insecure_channel("127.0.0.1:50001")
    # rpc_stub = SwitchmlIOStub(channel)
    # req = Sync.SendBarrierRequest(tensor_id=12345, node_id=1)
    # rpc_stub.SendBarrier(req)
    # print(req)
