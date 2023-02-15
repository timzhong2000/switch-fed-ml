from server import Server
from client import Client
from switch import Switch
import numpy as np
import time
from multiprocessing import Process

job_id = 100

def client_send():
    server = Server(
        node_id=3,
        ip_addr="11.11.11.3",
        rx_port=50000,
        tx_port=50001,
        rpc_addr="127.0.0.1:50001",
        is_remote_node=True)
    client = Client(
        node_id=1,
        ip_addr='11.11.11.1',
        rx_port=50000,
        tx_port=50001,
        rpc_addr="127.0.0.1:50000",
        is_remote_node=False,
        iface="veth1")
    data = np.random.rand((256)).astype(np.float32)
    packet_list = [
        client.create_packet(
            job_id=job_id,
            segment_id=0,
            group_id=1,
            bypass=False,
            data=data
        )
    ]
    print(data[0:5])
    client.send(
        server=server,
        job_id=job_id,
        packet_list=packet_list,
        has_switch=True
    )


def server_receive():
    server = Server(
        node_id=3,
        ip_addr="11.11.11.3",
        rx_port=50000,
        tx_port=50001,
        rpc_addr="127.0.0.1:50001",
        is_remote_node=False,
        iface="veth5")
    client = Client(
        node_id=1,
        ip_addr='11.11.11.1',
        rx_port=50000,
        tx_port=50001,
        rpc_addr="127.0.0.1:50000",
        is_remote_node=True)
    packet_list = server.receive(
        node=client,
        job_id=job_id,
        total_packet_num=1
    )
    print(packet_list[0].tensor[0:5])


p1 = Process(target=server_receive)
p2 = Process(target=client_send)

p1.start()
time.sleep(0.5)
p2.start()

p1.join()