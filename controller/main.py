import p4runtime_sh.shell as sh
from python_io.node import Node
from utils import *

sh.setup(
    device_id=0,
    grpc_addr='127.0.0.1:9559',
    election_id=(0, 1), # (high, low)
    config=sh.FwdPipeConfig('/root/switch-fed-ml/p4/switchfl.bmv2/p4info.txt', '/root/switch-fed-ml/p4/switchfl.bmv2/switchfl.json')
)

switch_addr = 0x0b0b0b00 # 11.11.11.0
switch_node_id = 0
ps_node_id = 3

def add_ps(egress_port: int, egress_rid: int, mcast_grp: int, ps_addr: int, ps_port: int):
    insert_mcast_replica(egress_port, egress_rid, mcast_grp)
    insert_ps_mark(egress_port, egress_rid)
    insert_reduce_address(egress_port, egress_rid, switch_addr, ps_addr, 50000, ps_port, switch_node_id)

def delete_ps(egress_port: int, egress_rid: int, mcast_grp: int):
    delete_mcast_replica(egress_port, egress_rid, mcast_grp)
    delete_ps_mark(egress_port, egress_rid)
    delete_reduce_address(egress_port, egress_rid)


def add_worker(egress_port: int, egress_rid: int, mcast_grp: int, worker_addr: int, worker_rx_port: int, worker_tx_port: int):
    insert_mcast_replica(egress_port, egress_rid, mcast_grp)
    insert_reduce_address(egress_port, egress_rid, switch_addr, worker_addr, 50000, worker_tx_port, switch_node_id)
    insert_multicast_address(egress_port, egress_rid, switch_addr, worker_addr, 50000, worker_rx_port, ps_node_id)
    
def del_worker(egress_port: int, egress_rid: int, mcast_grp: int):
    delete_mcast_replica(egress_port, egress_rid, mcast_grp)
    delete_reduce_address()
