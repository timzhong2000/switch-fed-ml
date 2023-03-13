
import sys
sys.path.append('./python_io')
sys.path.append('./prune')
import copy
from prune.cnn import SparseCNN
from exp.comm import EClient, EServer
from threading import Thread

model = SparseCNN({
    "conv1": (1, 32, 3),
    "conv1_channel_id": list(range(32)),
    "conv2": (32, 64, 3),
    "conv2_channel_id": list(range(64)),
    "fc1": (64 * 5 * 5, 128),
    "fc1_channel_id": list(range(128)),
    "fc2": (128, 10),
})

print(model)


def server():
    global model
    server = EServer(
        ip_addr="127.0.0.1",
        rx_port=50000,
        tx_port=50001,
        rpc_addr="127.0.0.1:50002",
        node_id=200,
        is_remote_node=False,
    )
    client = EClient(
        ip_addr="127.0.0.1",
        rx_port=50003,
        tx_port=50004,
        rpc_addr="127.0.0.1:50005",
        node_id=1,
        max_group_id=3,
        is_remote_node=True,
    )
    while server.round_id < 100:
        model_cp = copy.deepcopy(model)
        # do prune
        patches1 = model.prune(0.5)
        patches2 = model.prune(0.5)

        # multicast
        server.multicast_model(client, model, [patches1, patches2])
        
        # receive trained model
        model = server.receive_model(client)
        
        # do aggr
        diff = (model.conv1.weight-model_cp.conv1.weight).max()
        print("diff %f" % (diff))
        # next round
        server.round_id += 1


def client():
    server = EServer(
        ip_addr="127.0.0.1",
        rx_port=50000,
        tx_port=50001,
        rpc_addr="127.0.0.1:50002",
        node_id=200,
        is_remote_node=True,
    )
    client = EClient(
        ip_addr="127.0.0.1",
        rx_port=50003,
        tx_port=50004,
        rpc_addr="127.0.0.1:50005",
        node_id=1,
        max_group_id=3,
        is_remote_node=False,
    )
    while client.round_id < 100:

        model2 = client.receive_model(server)
        # do some training

        client.reduce_model(server, model2)
        client.round_id += 1

# diff = (model_cp.fc1.weight - model2.fc1.weight).max()
tc = Thread(target=client)
ts = Thread(target=server)

tc.start()
ts.start()
ts.join()
print("finish")
