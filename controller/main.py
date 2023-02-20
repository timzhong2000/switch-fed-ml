import p4runtime_sh.shell as sh
from utils.node import *
from utils.group import *

sh.setup(
    device_id=0,
    grpc_addr='127.0.0.1:9559',
    election_id=(0, 1),  # (high, low)
    config=sh.FwdPipeConfig('/root/switch-fed-ml/p4/switchfl.bmv2/p4info.txt',
                            '/root/switch-fed-ml/p4/switchfl.bmv2/switchfl.json')
)

switch_node_id = 10
ps_node_id = 99

switch_node = get_or_create_node(
    switch=sh,
    node_id=10,
    bitmap=-1,
    egress_port=-1,
    egress_rid=-1,
    mac="00:00:0b:0b:0b:08",
    addr="11.11.11.8",
    rx_port=50000,
    tx_port=50000,
    switch_node=None,
    ps_node_id=-1,
    role="switch"
)

ps_node = get_or_create_node(
    switch=sh,
    node_id=9,
    bitmap=-1,
    egress_port=1,
    egress_rid=1,
    mac="00:00:0b:0b:0b:09",
    addr="11.11.11.9",
    rx_port=50000,
    tx_port=50001,
    switch_node=switch_node,
    ps_node_id=9,
    role="ps"
)

node1 = get_or_create_node(
    switch=sh,
    node_id=1,
    bitmap=1,
    egress_port=0,
    egress_rid=1,
    mac="6a:c1:27:a9:ec:4e",
    addr="11.11.11.1",
    rx_port=50000,
    tx_port=50001,
    switch_node=switch_node,
    ps_node_id=ps_node.node_id,
)

node2 = get_or_create_node(
    switch=sh,
    node_id=2,
    bitmap=2,
    egress_port=0,
    egress_rid=2,
    mac="6a:c1:27:a9:ec:4f",
    addr="11.11.11.2",
    rx_port=50000,
    tx_port=50001,
    switch_node=switch_node,
    ps_node_id=ps_node.node_id,
)

group1 = get_or_create_group(
    switch=sh,
    mcast_grp=1,
    ps_node=ps_node
)
group2 = get_or_create_group(
    switch=sh,
    mcast_grp=2,
    ps_node=ps_node
)

node1.link_to_group(group1)

node1.link_to_group(group2)
node2.link_to_group(group2)
print("--------------------- config finish ---------------------------")
print("read_reduce_table: ")

node1.read_reduce_table()
