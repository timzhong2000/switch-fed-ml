from server import Server
from client import Client
import numpy as np
import time
from multiprocessing import Process

tensor_size = 256

def client_recv():
    server = Server("127.0.0.1", 50000, 50001, 50002, 3, True)
    client = Client('127.0.0.1', 50003, 50004, 50005, 1, False, "lo")
    tensor = np.zeros((tensor_size), dtype=np.float32)
    client.receive(server, 123, tensor)
    print("client %f" % (tensor[1]))


def server_send():
    server = Server("127.0.0.1", 50000, 50001, 50002, 3, False, "lo")
    client = Client('127.0.0.1', 50003, 50004, 50005, 1, True)
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
