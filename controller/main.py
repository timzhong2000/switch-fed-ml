import p4runtime_sh.shell as sh
from utils.switchfl_sender import *
from utils.switchfl_receiver import *

sh.setup(
    device_id=0,
    grpc_addr='127.0.0.1:9559',
    election_id=(0, 1), # (high, low)
    config=sh.FwdPipeConfig('/root/switch-fed-ml/p4/switchfl.bmv2/p4info.txt', '/root/switch-fed-ml/p4/switchfl.bmv2/switchfl.json')
)

switch_node_id = 10
ps_node_id = 99

receiver = Receiver(switch=sh)

receiver.init_group(
    ps_node_id=ps_node_id,
    mcast_grp=1,
    egress_port=2,
    egress_rid=0
)
receiver.add_worker_to_group(
    node_id=1,
    mcast_grp=1,
    egress_port=0,
    egress_rid=1,
    node_bitmap=1
)

# receiver.init_group(
#     ps_node_id=ps_node_id,
#     mcast_grp=2,
#     egress_port=2,
#     egress_rid=0
# )
# receiver.add_worker_to_group(
#     node_id=1,
#     mcast_grp=2,
#     egress_port=0,
#     egress_rid=1,
#     node_bitmap=1
# )
# receiver.add_worker_to_group(
#     node_id=2,
#     mcast_grp=2,
#     egress_port=0,
#     egress_rid=2,
#     node_bitmap=2
# )


sender = Sender(
    switch=sh, 
    switch_node_id=switch_node_id, 
    switch_mac="00:00:0b:0b:0b:00"
)

sender.add_node(
    node_id=1,
    node_mac="6a:c1:27:a9:ec:4e",
    egress_port=0,
    egress_rid=1,
    switch_addr="11.11.11.0",
    switch_port=51000,
    node_address="11.11.11.1",
    rx_port=50000,
    tx_port=50001,
    ps_node_id=ps_node_id,
    is_ps=False
)
sender.add_node(
    node_id=2,
    node_mac="6a:c1:27:a9:ec:4e",
    egress_port=0,
    egress_rid=2,
    switch_addr="11.11.11.0",
    switch_port=51000,
    node_address="11.11.11.2",
    rx_port=50003,
    tx_port=50004,
    ps_node_id=ps_node_id,
    is_ps=False
)
sender.add_node(
    node_id=ps_node_id,
    node_mac="6a:c1:27:a9:ec:4e",
    egress_port=2,
    egress_rid=1,
    switch_addr="11.11.11.0",
    switch_port=51000,
    node_address="11.11.11.3",
    rx_port=50000,
    tx_port=50001,
    ps_node_id=ps_node_id,
    is_ps=False
)

print("--------------------- config finish ---------------------------")
print("read_reduce_table: ")
sender.read_reduce_table()