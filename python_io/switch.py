from node import Node
class Switch(Node):
  def __init__(self, ip_addr: str, rx_port: int, tx_port: int, rpc_port: int, node_id: int, is_remote_node: bool):
    super().__init__(ip_addr, rx_port, tx_port, rpc_port, node_id, is_remote_node)
    self.type = "switch"