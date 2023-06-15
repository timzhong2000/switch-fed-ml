import python_path
from multiprocessing import Process, Barrier
import argparse
from start_client import start_client
from start_switch import start_switch
from start_server import start_server
from throttle import throttle
import torch

torch.manual_seed(0)

# args
parser = argparse.ArgumentParser(prog="client_test")
parser.add_argument(
    '-t',
    '--type',
    help="通信库类型，可选 switchfl",
    default="switchfl"
)
parser.add_argument(
    '-r',
    '--round',
    type=int,
    default=10
)
parser.add_argument(
   '-n',
   "--nodenum",
   type=int,
   default=1
)
parser.add_argument(
   '-s',
   "--server_throttle_scale",
   type=int,
   default=1
)
parser.add_argument(
    '--commlib',
    default="sfl"
)
parser.add_argument(
   "--dryrun",
   type=bool
)
args = parser.parse_args()
# DEBUG
args.commlib = "tcp"

# config
ROUND = args.round
max_group_num = 4

node_num = args.nodenum
mock_switch_config = {
    "node_id": 101,
    "ip_addr": "127.0.0.1",
    "port": 30000,
    "rpc_addr": "127.0.0.1:30002"
}
server_config = {
    "node_id": 100,
    "ip_addr": "127.0.0.1",
    "rx_port": 50000,
    "tx_port": 50001,
    "rpc_addr": "127.0.0.1:50002",
}
__clients = [
    {
        "node_id": i + 1,
        "ip_addr": "127.0.0.1",
        "rx_port": 50003 + i * 3,
        "tx_port": 50004 + i * 3,
        "rpc_addr": "127.0.0.1:%d" % (50005 + i * 3),
        "max_group": i % max_group_num + 1,
        "bitmap": 1 << i
    } for i in range(node_num)
]
clients_config = {}
for config in __clients:
    clients_config[config["node_id"]] = config


# run

## 限速
throttle(10, node_num, args.server_throttle_scale)
## sync
multicast_barrier = Barrier(node_num + 1)
reduce_barrier = Barrier(node_num + 1)
## start switch
switch = Process(target=start_switch, args=(server_config, clients_config, mock_switch_config, max_group_num))
switch.start()
## start clients
for config in clients_config.values():
  client = Process(target=start_client, args=(ROUND, config, server_config, mock_switch_config, multicast_barrier, reduce_barrier, config['node_id']-1, node_num, args.commlib, args.dryrun))
  client.start()
## start server
server = Process(target=start_server, args=(ROUND, server_config, mock_switch_config, clients_config, multicast_barrier, reduce_barrier, args.commlib, args.dryrun))
server.start()
server.join()