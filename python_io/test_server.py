from server import Server
from client import Client
import numpy as np

if __name__ == '__main__':
    # 256 * int32 = 1KB
    tensor = np.zeros((1024 * 256), dtype=np.int32)

    node_id = 1
    server = Server("127.0.0.1", 50000, 50001, 50002, 0, False)
    client = Client('127.0.0.1', 50000+node_id*3,
                    50000+node_id*3+1, 50000+node_id*3+2, node_id, True)
    while True:
        server.receive(client, 0, 12345, tensor)
        print(tensor)

    server.close()
    print("finish")