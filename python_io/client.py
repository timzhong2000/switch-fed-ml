from node import Node

class Client(Node):
    def __init__(self, ip_addr: str, port: int, rpc_port: int, node_id: int, is_remote_node: bool):
        super().__init__(ip_addr, port, rpc_port, node_id, is_remote_node)
