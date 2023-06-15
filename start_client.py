import time
from exp.comm import EClient, EServer
from sparse_model.utils import train_model
from sparse_model.dataset.mnist import trainloader
from tcp_comm import TCPClient

recv_time = []
reduce_time = []

def round(server, client, multicast_barrier, reduce_barrier, client_index: int, max_client: int, dry_run = False):
    print("start receive")
    multicast_barrier.wait()
    recv_start = time.time()
    time.sleep(0.2)
    model = client.receive_model(server)
    recv_end = time.time()
    recv_time.append(recv_end - recv_start - 0.2)

    if dry_run:
        pass
    else:
        train_start = time.time()
        train_model(model, trainloader, max_client, client_index)
        train_end = time.time()
        print("train time", train_end - train_start)

    reduce_barrier.wait()
    print("start reduce")
    reduce_start = time.time()
    time.sleep(0.2)
    client.reduce_model(server, model)
    reduce_end = time.time()
    reduce_time.append(reduce_end - reduce_start - 0.2)
    print("recv_time = %f \treduce_time = %f" %
          (recv_end - recv_start, reduce_end - reduce_start))


def start_client(ROUND: int, client_config: dict, server_config: dict, mock_switch_config: dict, multicast_barrier, reduce_barrier, client_index, max_client, comm = "sfl", dry_run: bool = False):
    if comm == "tcp":
        client = TCPClient(server_config, client_config)
        server = None
    else:
        client = EClient(
            node_id=client_config['node_id'],
            ip_addr=client_config['ip_addr'],
            rx_port=client_config['rx_port'],
            tx_port=client_config['tx_port'],
            rpc_addr=client_config['rpc_addr'],
            max_group_id=client_config['max_group'],
            is_remote_node=False,
        )

        server = EServer(
            node_id=server_config['node_id'],
            ip_addr=server_config['ip_addr'],
            rx_port=mock_switch_config['port'],
            tx_port=server_config['tx_port'],
            rpc_addr=server_config['rpc_addr'],
            is_remote_node=True,
        )

    while client.round_id < ROUND:
        print("------------------ ROUND %d START -----------------------" %
              (client.round_id))
        round(server, client, multicast_barrier, reduce_barrier, client_index, max_client, dry_run)
        print("------------------ ROUND %d END -------------------------" %
              (client.round_id))
        client.round_id += 1

    print(recv_time)
    print(reduce_time)
