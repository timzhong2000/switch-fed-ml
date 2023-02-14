# python_io
Switch FL 通信库 python 实现

## 基本概念
1. rx_port: 数据接收端口
2. tx_port: 数据发送端口，不支持并行数据发送
3. rpc_addr: grpc 服务监听地址
4. is_remote_node: 是否是远端节点，在 SwitchFL io 模块中，有远端节点和本地节点的概念，如果是本地节点，在实例化时会监听 `rx_port` `tx_port` 并且启动 `grpc` 服务，因此强烈推荐且目前只能单例。对于远端节点，在实例化时会创建 `grpc` stub 实例，因此对于一个远端节点可以创建多个实例，但仍然建议单例。
5. switch_pool_size: switch 开启的聚合器数量，聚合过程中发送窗口必须等于这个值才能最高效利用 switch。
6. packet: 数据分发的最小单位，一个包有效载荷长度为 1KB
