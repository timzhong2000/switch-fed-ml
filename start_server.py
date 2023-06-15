from pyinstrument import Profiler
from torchsummary import summary
from sparse_model.vgg import SparseVGG, example_vgg_meta
from sparse_model.cnn import SparseLeNet
from switch import Switch
from exp.comm import EClient, EServer
import time
from sparse_model.utils import test_model
from sparse_model.dataset.mnist import testloader
from tcp_comm import TCPServer
import copy
# 测试代码
# model = SparseVGG(example_vgg_meta)
# model.prune(0.75)
model = SparseLeNet({
    "conv1": (1, 32, 3),
    "conv1_channel_id": list(range(32)),
    "conv2": (32, 64, 3),
    "conv2_channel_id": list(range(64)),
    "fc1": (5*5*64, 1024),
    "fc1_channel_id": list(range(1024)),
    "fc2": (1024, 10),
    "pic_size": 5*5
})

reduce_time = []
send_time = []

summary(model, (1, 28, 28))

max_group_num = 4

def round(server, switch, multicast_barrier, reduce_barrier, dry_run: bool = False):
    global model
    model_copy = copy.deepcopy(model)

    profiler = Profiler()
    profiler.start()
    send_start = time.time()
    patches_list = []
    for i in range(max_group_num - 1):
        patches_list.append(model.prune(0.25))
    multicast_barrier.wait()
    server.multicast_model(switch, model, patches_list)

    send_end = time.time()
    send_time.append(send_end - send_start)

    reduce_barrier.wait()
    reduce_start = time.time()
    if dry_run:
        server.receive_model(switch)
        model = model_copy
    else:
        model = server.receive_model(switch)
    reduce_end = time.time()
    reduce_time.append(reduce_end - reduce_start)
    profiler.stop()
    profiler.print()

    # test_model(model, testloader)

    print("send_time = %f \treduce_time = %f" %
          (send_end - send_start, reduce_end - reduce_start))


def start_server(ROUND: int, server_config: dict, mock_switch_config: dict, clients_config: dict, multicast_barrier, reduce_barrier, comm = "sfl", dry_run: bool = False):
    if comm == "tcp":
        server = TCPServer(server_config, clients_config)
        switch = None
    else:
        server = EServer(
            node_id=server_config['node_id'],
            ip_addr=server_config['ip_addr'],
            rx_port=server_config['rx_port'],
            tx_port=server_config['tx_port'],
            rpc_addr=server_config['rpc_addr'],
            is_remote_node=False,
        )

        switch = Switch(
            node_id=mock_switch_config['node_id'],
            ip_addr=mock_switch_config['ip_addr'],
            rx_port=mock_switch_config['port'],
            tx_port=mock_switch_config['port'],
            rpc_addr=mock_switch_config['rpc_addr']
        )

        for config in clients_config.values():
            switch.add_child(
                EClient(
                    node_id=config["node_id"],
                    ip_addr=config["ip_addr"],
                    rx_port=config["rx_port"],
                    tx_port=config["tx_port"],
                    rpc_addr=config["rpc_addr"],
                    max_group_id=config["max_group"],
                    is_remote_node=True,
                )
            )

    while server.round_id < ROUND:
        print("------------------ ROUND %d START -----------------------" %
              (server.round_id))
        round(server, switch, multicast_barrier, reduce_barrier, dry_run)
        print("------------------ ROUND %d END -------------------------" %
              (server.round_id))
        server.round_id += 1
    print(send_time)
    print(reduce_time)
