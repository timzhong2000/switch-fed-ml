import mock_switch.switch
import mock_switch.node
import mock_switch.group

def start_switch(server_config, clients_config, mock_switch_config, max_group_num):
    mock_switch_instance = mock_switch.switch.Switch(
        addr=mock_switch_config['ip_addr'],
        port=mock_switch_config['port'],
        node_id=mock_switch_config['node_id'],
        debug=False
    )

    # 创建 ps 实例
    ps = mock_switch.node.Node(
        id=server_config['node_id'],
        ip_addr=server_config['ip_addr'],
        rx_port=server_config['rx_port'],
        tx_port=server_config['tx_port'],
        bitmap=0
    )
    mock_switch_instance.nodes[ps.id] = ps

    # 注册组
    for i in range(1, max_group_num + 1):
        g = mock_switch.group.Group(i, ps)
        mock_switch_instance.groups[g.id] = g

    # 创建 client 实例
    for config in clients_config.values():
        node = mock_switch.node.Node(
            id=config['node_id'],
            ip_addr=config['ip_addr'],
            rx_port=config['rx_port'],
            tx_port=config['tx_port'],
            bitmap=config['bitmap']
        )
        for i in range(1, config["max_group"] + 1):
            mock_switch_instance.groups[i].addNode(node)
        mock_switch_instance.nodes[node.id] = node
    print("start switch...")
    mock_switch_instance.start()