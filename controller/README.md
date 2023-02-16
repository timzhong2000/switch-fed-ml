# SwitchFL control plane
## 介绍
P4Runtime controller，用于读写 switch 的表项，配置剪枝参数和节点网络转发地址

## 基本用法
### 节点 Node

**对于 SwitchFL，存在多种节点**

1. role="ps" 参数服务器，参数服务器需要提供完整的节点网络地址信息，在分组聚合完成时将会向参数服务器发送完整数据包，向工作节点发送 ack 包
2. role="switch" 交换机，对于每个工作节点，需要提供直连的交换机信息，用于完成 WAN <=> LAN 转发
3. role=其他  工作节点，工作节点需要提供完整的节点网络地址信息，在下发时会向工作节点发送完整数据包，向 ps 发送 ack 包

**节点初始化**

```py
switch_node = get_or_create_node(
    switch=sh,
    node_id=10,
    bitmap=-1,                      # switch 不需要 bitmap 信息
    egress_port=-1,                 # switch 不需要 egress_port 信息
    egress_rid=-1,                  # switch 不需要 egress_rid 信息
    mac="00:00:0b:0b:0b:08",
    addr="11.11.11.8",
    rx_port=50000,
    tx_port=50000,
    switch_node=None,               # switch 不需要直连 switch 信息
    ps_node_id=-1,                  # switch 不需要 ps_node_id 信息
    role="switch"
)

ps_node = get_or_create_node(
    switch=sh,
    node_id=9,
    bitmap=-1,                      # ps 不需要 bitmap 信息
    egress_port=2,
    egress_rid=1,
    mac="00:00:0b:0b:0b:09",
    addr="11.11.11.9",
    rx_port=50000,
    tx_port=50001,
    switch_node=switch_node,
    ps_node_id=9,
    role="ps"
)

worker = get_or_create_node(
    switch=sh,
    node_id=1,
    bitmap=1,
    egress_port=0,
    egress_rid=1,
    mac="00:00:0b:0b:0b:01",
    addr="11.11.11.1",
    rx_port=50000,
    tx_port=50001,
    switch_node=switch_node,
    ps_node_id=ps_node.node_id,
)
```

### 分组 Group

**基本用法**

```py
group1 = get_or_create_group(sh, 1, ps_node)
# 将 worker 添加到分组 1
worker.link_to_group(group1) 
# 将 worker 从分组 1 移除
worker.unlink_to_group(group1) 

```