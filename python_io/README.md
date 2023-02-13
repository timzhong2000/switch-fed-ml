# python_io
Switch FL 通信库 python 实现

## 基本概念
1. rx_port: 数据接收端口
2. tx_port: 数据发送端口，不支持并行数据发送
3. rpc_port: grpc 服务端口
4. is_remote_node: 是否是远端节点，在 SwitchFL io 模块中，有远端节点和本地节点的概念，如果是本地节点，在实例化时会监听 `rx_port` `tx_port` 并且启动 `grpc` 服务，因此强烈推荐且目前只能单例。对于远端节点，在实例化时会创建 `grpc` stub 实例，因此对于一个远端节点可以创建多个实例，但仍然建议单例。
5. switch_pool_size: switch 开启的聚合器数量，聚合过程中发送窗口必须等于这个值才能最高效利用 switch。
6. tensor: 目前为 np.ndarray，可以是任意长度的一维 float32 向量。暂时仅支持 float32 向量。

## 用法

Server 从 Client 接收向量

Server
- ip=127.0.0.1
- rx_port=50000
- tx_port=50001
- rpc_port=50002
- node_id=3
- bind_iface="lo"

Client
- ip=127.0.0.1
- rx_port=50003
- tx_port=50004
- rpc_port=50005
- node_id=1
- bind_iface="lo"

Server 实现
```py
tensor_size = 1024
server = Server("127.0.0.1", 50000, 50001, 50002, 3, False, "lo")
client = Client('127.0.0.1', 50003, 50004, 50005, 1, True)
tensor = np.zeros((tensor_size), dtype=np.float32)
server.receive(client, 123, tensor)
print(tensor[0:5])
```

Client 实现
```py
tensor_size = 1024
server = Server("127.0.0.1", 50000, 50001, 50002, 3, True)
client = Client('127.0.0.1', 50003, 50004, 50005, 1, False, "lo")
tensor = np.random.rand((tensor_size)).astype(np.float32)
print(tensor[0:5])
client.send(server, 2, 123, tensor, False)
```