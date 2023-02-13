from server import Server
from client import Client
import numpy as np
import time
from multiprocessing import Process

tensor_size = 256 * 1024 * 10

def client_send():
    server = Server("127.0.0.1", 50000, 50001, 50002, 3, True)
    client = Client('127.0.0.1', 50003, 50004, 50004, 1, False, "lo")
    tensor = np.random.rand((tensor_size)).astype(np.float32)
    print(tensor[0:5])
    client.send(server, 2, 123, tensor, False)

def server_receive():
    server = Server("127.0.0.1", 50000, 50001, 50002, 3, False, "lo")
    client = Client('127.0.0.1', 50003, 50004, 50004, 1, True)
    tensor = np.zeros((tensor_size), dtype=np.float32)
    server.receive(client, 123, tensor)
    print(tensor[0:5])

p1 = Process(target=server_receive)
p2 = Process(target=client_send)

p1.start()
time.sleep(0.5)
p2.start()

p1.join()