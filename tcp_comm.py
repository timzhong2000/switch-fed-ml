"""
config 兼容 switchfl 格式， tcp 监听端口为 rxport
"""
import time
import python_path
import socket
import pickle
from threading import Thread
from sparse_model.cnn import SparseLeNet
import torch
from multiprocessing import Process, Barrier
from sparse_model.utils import test_model, train_model
from sparse_model.dataset.mnist import testloader,trainloader
from throttle import throttle
import s3

torch.manual_seed(0)
ROUND = 10
node_num = 1
max_groud_id = 2
multicast_barrier = Barrier(node_num + 1)
reduce_barrier = Barrier(node_num + 1)
buffer_size = 4096

def send(sock: socket.socket, data):
    sock.send(data)

def recv(sock: socket.socket):
    buffer = b''
    while True:
        data = sock.recv(buffer_size)
        if not data:
            break
        buffer += data
    return buffer

class TCPServer:
    def __init__(self, server_config, clients_config) -> None:
        self.server_config = server_config
        self.clients_config = clients_config
        self.round_id = 0
        self.last_patches_list = []

    def init_conn(self):
        # conn init
        print("start init_conn")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.server_config['ip_addr'], self.server_config['rx_port']))
        sock.listen(len(self.clients_config))
        clients = [sock.accept()[0] for _ in self.clients_config]
        print("end init_conn")
        return sock, clients
        
    def close_conn(self, sock, clients):
        # conn close
        for c in clients:
            c.close()
        sock.close()

    def multicast_model(self, node, model, patches_list):
        """
        models: 分发给不同组的模型
        """
        sock, clients = self.init_conn()

        self.last_patches_list = patches_list
        # 恢复模型
        data = [pickle.dumps(model)]
        for patches in reversed(patches_list):
            model.apply_patches(patches)
            data.append(pickle.dumps(model))

        threads = []
        for sock, config in zip(clients, self.clients_config.values()):
            threads.append(Thread(target=send, args=(
                sock, data[config['max_group'] - 1], )))
            threads[-1].start()
        for t in threads:
            t.join()
        self.close_conn(sock, clients)
        
        # # s3 mcast
        # s3.server_send(self.round_id, data)

    def receive_model(self, node):
        sock, clients = self.init_conn()
        
        # tcp recv
        buffer = [None] * len(clients)
        def _recv(sock: socket.socket, config):
            nid = config['node_id']
            buffer[nid-1] = pickle.loads(recv(sock))

            
        threads = []
        for sock, config in zip(clients, self.clients_config.values()):
            threads.append(Thread(target=_recv, args=(sock, config,)))
            threads[-1].start()
        for t in threads:
            t.join()

        # # s3 recv
        # for i, config in enumerate(self.clients_config):
        #     buffer[i] = pickle.loads(s3.server_recv(config, self.round_id))
        
        
        # # aggr
        # # 实验代码，硬编码
        # mini_model_list = []
        # # patches1_list = []
        # # patches2_list = []
        # patches3_list = []
        # for model, config in zip(buffer, self.clients_config.values()):
        #     # if config['max_group'] == 4:
        #     #     patches1_list.append(model.redo_prune(self.last_patches_list[0]))
        #     #     patches2_list.append(model.redo_prune(self.last_patches_list[1]))
        #     #     patches3_list.append(model.redo_prune(self.last_patches_list[2]))
        #     #     pass
        #     # if config['max_group'] == 3:
        #     #     patches2_list.append(model.redo_prune(self.last_patches_list[1]))
        #     #     patches3_list.append(model.redo_prune(self.last_patches_list[2]))
        #     #     pass
        #     if config['max_group'] == 2:
        #         patches3_list.append(model.redo_prune(self.last_patches_list[0]))
        #         pass
        #     if config['max_group'] == 1:
        #         pass
        #     mini_model_list.append(model)
        #     pass
        # mini_model = mini_model_list[0]
        # for i in range(1, len(mini_model_list)):
        #     mini_model += mini_model_list[i]
        # mini_model /= len(mini_model_list)

        # # patches1 = patches1_list[0]
        # # for i in range(1, len(patches1_list)):
        # #     patches1 += patches1_list[i]
        # # patches1 /= len(patches1_list)

        # # patches2 = patches2_list[0]
        # # for i in range(1, len(patches2_list)):
        # #     patches2 += patches2_list[i]
        # # patches2 /= len(patches2_list)
        
        # patches3 = patches3_list[0]
        # for i in range(1, len(patches3_list)):
        #     patches3 += patches3_list[i]
        # for i in patches3:
        #     i /= len(patches3_list)
        
        # mini_model.apply_patches(patches3)
        # # mini_model.apply_patches(patches2)
        # # mini_model.apply_patches(patches1)

        self.close_conn(sock, clients)
        
        return None


class TCPClient:
    def __init__(self, server_config, client_config) -> None:
        self.server_config = server_config
        self.client_config = client_config
        self.round_id = 0

    def reduce_model(self, server, model):
        # tcp send
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.server_config['ip_addr'], self.server_config['rx_port']))
        send(sock, pickle.dumps(model))

        # # s3 send
        # s3.sendback(self.client_config, self.round_id, data)

    def receive_model(self, server):
        # tcp recv
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.server_config['ip_addr'], self.server_config['rx_port']))
        sparse_model = pickle.loads(recv(sock))

        # # s3 recv
        # sparse_model = pickle.loads(s3.client_recv(self.client_config, self.round_id))

        return sparse_model

if __name__ == "__main__":
    throttle(10, node_num, 2)

    server_config = {
        "node_id": 100,
        "rx_port": 50000,
        "ip_addr": "127.0.0.1"
    }
    clients_config = [
        {
          "node_id": i + 1,
          "rx_port": 50003 + i * 3,
          "ip_addr": "127.0.0.1",
          "max_group": i % max_groud_id + 1
        } for i in range(node_num)
    ]
    clients = []
    def s(multicast_barrier, reduce_barrier):
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

        server = TCPServer(server_config, clients_config)
        for i in range(ROUND):
            print("------------------ ROUND %d START -----------------------" % i)
            patches3 = model.prune(0.25) 
            patches_list = [patches3]
            multicast_barrier.wait()
            server.multicast_model(None, model, patches_list)
            reduce_barrier.wait()
            model = server.receive_model(None)
            test_model(model, testloader)
            print("------------------ ROUND %d END -----------------------" % i)
        
    def c(config, multicast_barrier, reduce_barrier):
        client = TCPClient(server_config, config)
        clients.append(client)
        for i in range(ROUND):
            time.sleep(0.5)
            multicast_barrier.wait()
            recv_start = time.time()
            model = client.receive_model(None)
            recv_end = time.time()
            print("recv_finish", recv_end - recv_start)
            print("client model", model)
            train_model(model, trainloader, node_num, config['node_id'] - 1, 1)
            reduce_barrier.wait()
            time.sleep(0.5)
            client.reduce_model(None, model)

    st = Process(target=s, args=(multicast_barrier, reduce_barrier))
    st.start()
    for config in clients_config:
        Process(target=c, args=(config, multicast_barrier, reduce_barrier)).start()

    st.join()
