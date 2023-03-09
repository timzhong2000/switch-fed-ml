from server import Server
from client import Client
from switch import Switch
import numpy as np
import time
from multiprocessing import Process

round_id = 101
pkt_num = 10000

server_node_id = 10
server_ip_addr = "127.0.0.1"
server_rx_port = 50000
server_tx_port = 50001
server_rpc_addr = "127.0.0.1:50002"

mock_switch_node_id = 9
mock_switch_ip_addr = "127.0.0.1"
mock_switch_port = 30000

client_node_id = 1
client_ip_addr = "127.0.0.1"
client_rx_port = 50003
client_tx_port = 50004
client_rpc_addr = "127.0.0.1:50005"


def client_send():
    server = Server(
        node_id=server_node_id,
        ip_addr=server_ip_addr,

        # rx_port=server_rx_port,
        rx_port=mock_switch_port,

        tx_port=server_tx_port,
        rpc_addr=server_rpc_addr,
        is_remote_node=True
    )
    client = Client(
        node_id=client_node_id,
        ip_addr=client_ip_addr,
        rx_port=client_rx_port,
        tx_port=client_tx_port,
        rpc_addr=client_rpc_addr,
        is_remote_node=False,
        # iface="veth1"
    )
    data = np.random.rand((256 * pkt_num)).astype(np.float32)
    packet_list = [client.create_packet(
        round_id=round_id,
        segment_id=i,
        group_id=1,
        bypass=False,
        data=data[256*i: 256*(i+1)]
    ) for i in range(pkt_num)]
    print(data[0:5])
    client.send(
        server=server,
        round_id=round_id,
        packet_list=packet_list,
        has_switch=True
    )


def server_receive():
    server = Server(
        node_id=server_node_id,
        ip_addr=server_ip_addr,
        rx_port=server_rx_port,
        tx_port=server_tx_port,
        rpc_addr=server_rpc_addr,
        is_remote_node=False,
        # iface="veth5"
    )
    client = Client(
        node_id=client_node_id,
        ip_addr=client_ip_addr,
        rx_port=client_rx_port,
        tx_port=client_tx_port,
        rpc_addr=client_rpc_addr,
        is_remote_node=True
    )
    switch = Switch(
        node_id=mock_switch_node_id,
        ip_addr=mock_switch_ip_addr,
        rx_port=mock_switch_port,
        tx_port=mock_switch_port,
        rpc_addr=""
    )
    switch.add_child(client)
    packet_list = server.receive(
        node=switch,
        round_id=round_id,
        total_packet_num=pkt_num
    )
    print(packet_list[0].tensor[0:5])


p1 = Process(target=server_receive)
p2 = Process(target=client_send)

p1.start()
time.sleep(0.5)
p2.start()

p1.join()
