from server import Server
from client import Client
import numpy as np
import time
from multiprocessing import Process

tensor_size = 10 * 1024 * 256


def client_recv():
    server = Server(ip_addr="11.11.11.3",
                    rx_port=50000,
                    tx_port=50001,
                    rpc_addr="127.0.0.1:50001",
                    node_id=3,
                    is_remote_node=True)
    client = Client(ip_addr='11.11.11.1',
                    rx_port=50000,
                    tx_port=50004,
                    rpc_addr="127.0.0.1:50000",
                    node_id=1,
                    is_remote_node=False,
                    iface="lo")
    tensor = np.zeros((tensor_size), dtype=np.float32)
    client.receive(server, 123, tensor)
    print("client %f" % (tensor[1]))


def server_send():
    server = Server(ip_addr="11.11.11.3",
                    rx_port=50000,
                    tx_port=50001,
                    rpc_addr="127.0.0.1:50001",
                    node_id=3,
                    is_remote_node=False,
                    iface="veth3")
    switch = Switch(ip_addr='11.11.11.1',
                    rx_port=50000,
                    tx_port=50004,
                    rpc_addr="127.0.0.1:50000",
                    node_id=1,
                    is_remote_node=True)
    tensor = np.random.rand((tensor_size)).astype(np.float32)
    print("server %f" % (tensor[1]))
    server.send(client, 2, 123, tensor)


p1 = Process(target=client_recv)
p2 = Process(target=server_send)

p1.start()
time.sleep(0.5)
p2.start()

p1.join()
p2.join()
