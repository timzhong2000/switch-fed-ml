import p4runtime_sh.shell as sh
from utils.pre import *

sh.setup(
    device_id=0,
    grpc_addr='127.0.0.1:9559',
    election_id=(0, 1), # (high, low)
    config=sh.FwdPipeConfig('/root/switch-fed-ml/p4/switchfl.bmv2/p4info.txt', '/root/switch-fed-ml/p4/switchfl.bmv2/switchfl.json')
)

# port 0: node 0      ip 11.11.11.1
# port 1: node 1      ip 11.11.11.2
# port 2: ps(node 2)  ip 11.11.11.3

insert_mcast_replicas([
    {"egress_port": 0, "egress_rid": 1}, 
    {"egress_port": 1, "egress_rid": 1},
    {"egress_port": 2, "egress_rid": 1},
  ], 2)

mcge = sh.MulticastGroupEntry(2)
mcge.read(lambda c: print(c))