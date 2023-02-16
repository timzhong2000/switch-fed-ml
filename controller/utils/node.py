import p4runtime_sh.shell as p4sh

__node_cache_map = {}  # Map<node_id, Node>


class Node():
    def __init__(self, switch: p4sh, node_id: int, bitmap: int, egress_port: int, egress_rid: int, mac: str, addr: str, rx_port: int, tx_port: int, switch_node, ps_node_id, role: str, dryRun=False) -> None:

        self.switch = switch
        self.node_id = node_id
        self.bitmap = bitmap
        self.egress_port = egress_port
        self.egress_rid = egress_rid
        self.mac = mac
        self.addr = addr
        self.rx_port = rx_port
        self.tx_port = tx_port
        self.switch_node: Node = switch_node
        self.ps_node_id = ps_node_id
        self.role = role

        self.__dryRun = dryRun

        self.group_map = {}  # mcast_grp => Group

    def apply(self):
        if self.role == "switch":
            return
        if self.role == "ps":
            self.__insert_ps_mark()
        else:
            self.__insert_worker_bitmap()
        self.__insert_multicast_address()
        self.__insert_reduce_address()

    def reset(self):
        if self.role == "switch":
            return
        if self.role == "ps":
            self.__delete_ps_mark()
        else:
            self.__delete_worker_bitmap()
        self.__delete_multicast_address()
        self.__delete_reduce_address()

    def delete(self):
        self.reset()
        del __node_cache_map[self.node_id]
        for group in self.group_map.values():
            self.unlink_to_group(group)

    def link_to_group(self, group):
        self.group_map[group.mcast_grp] = group
        group.node_map[self.node_id] = self
        group.reset()
        group.apply()

    def unlink_to_group(self, group):
        if self.group_map.get(group.mcast_grp) is None or group.node_map.get(self.node_id) is None:
            print("group %d is not linked to this node")
            return
        del self.group_map[group.mcast_grp]
        del group.node_map[self.node_id]
        group.reset()
        group.apply()

    # 从 header.node_id 到聚合器识别的 node bitmap 的映射
    def __insert_worker_bitmap(self):
        if self.__dryRun:
            print("[Receiver Controller] __insert_worker_bitmap node_id=%d, node_bitmap=%d" % (
                self.node_id, self.bitmap))
            return
        te = self._get_worker_bitmap_table_entry(
            self.node_id)(action='set_bitmap')
        te.action.set(bitmap=str(self.bitmap))
        te.insert()

    def __delete_worker_bitmap(self):
        if self.__dryRun:
            print("[Receiver Controller] __delete_worker_bitmap node_id=%d" %
                  (self.node_id))
            return
        self._get_worker_bitmap_table_entry(self.node_id).delete()

    def _get_worker_bitmap_table_entry(self, node_id: int):
        te = self.switch.TableEntry(
            'MyIngress.switchfl_receiver.worker_bitmap')
        te.match['hdr.switchfl.node_id'] = str(node_id)
        return te

    def __insert_ps_mark(self):
        if self.__dryRun:
            return
        self._get_ps_mark_table_entry()(action='set_is_ps').insert()

    def __delete_ps_mark(self):
        if self.__dryRun:
            return
        self._get_ps_mark_table_entry().delete()

    def __insert_reduce_address(self):
        dst_port = self.rx_port if self.role == "ps" else self.tx_port

        if self.__dryRun:
            print("[Sender Controller] __insert_reduce_address [egress_port=%d, egress_rid=%d] => src=%s:%d (%s), dst=%s:%d (%s), rewrite_node_id=%d" % (
                self.egress_port, self.egress_rid, self.switch_node.addr, self.switch_node.rx_port, self.switch_node.mac, self.addr, dst_port, self.mac, self.node_id))
            return
        te = self._get_reduce_table_entry()(action='set_dest')
        te.action.set(
            src_mac=self.switch_node.mac,
            dst_mac=self.mac,
            src_addr=self.switch_node.addr,
            src_port=str(self.switch_node.rx_port),
            dst_addr=self.addr,
            dst_port=str(dst_port),
            node_id=str(self.switch_node.node_id)
        )
        te.insert()

    def __delete_reduce_address(self, egress_port: int, egress_rid: int):
        if self.__dryRun:
            print("[Sender Controller] __delete_reduce_address [egress_port=%d, egress_rid=%d]" % (
                egress_port, egress_rid))
            return
        self._get_reduce_table_entry().delete()

    def __insert_multicast_address(self):
        dst_port = self.tx_port if self.role == "ps" else self.rx_port

        if self.__dryRun:
            print("[Sender Controller] __insert_multicast_address [egress_port=%d, egress_rid=%d] => src=%s:%d (%s), dst=%s:%d (%s), rewrite_node_id=%d" % (
                self.egress_port, self.egress_rid, self.switch_node.addr, self.switch_node.tx_port, self.switch_node.mac, self.addr, dst_port, self.mac, self.ps_node_id))
            return
        te = self._get_multicast_table_entry()(action='set_dest')
        te.action.set(
            src_mac=self.switch_node.mac,
            dst_mac=self.mac,
            src_addr=self.switch_node.addr,
            src_port=str(self.switch_node.tx_port),
            dst_addr=self.addr,
            dst_port=str(dst_port),
            node_id=str(self.ps_node_id)
        )
        te.insert()

    def __delete_multicast_address(self):
        if self.__dryRun:
            print("[Sender Controller] __delete_multicast_address [egress_port=%d, egress_rid=%d]" % (
                self.egress_port, self.egress_rid))
            return
        self._get_multicast_table_entry().delete()

    def _get_ps_mark_table_entry(self):
        te = self.switch.TableEntry('MyEgress.switchfl_sender.ps_mark')
        self.__set_table_match(te)
        return te

    def _get_reduce_table_entry(self):
        te = self.switch.TableEntry(
            'MyEgress.switchfl_sender.switchfl_reduce_address')
        self.__set_table_match(te)
        return te

    def _get_multicast_table_entry(self):
        te = self.switch.TableEntry(
            'MyEgress.switchfl_sender.switchfl_multicast_address')
        self.__set_table_match(te)
        return te

    def __set_table_match(self, te: p4sh.TableEntry):
        te.match['standard_meta.egress_port'] = str(self.egress_port)
        te.match['standard_meta.egress_rid'] = str(self.egress_rid)

    def read_reduce_table(self, callback=None):
        """
        - callback: call on each TableEntry
        """
        self.switch.TableEntry('MyEgress.switchfl_sender.switchfl_reduce_address').read(
            callback if callback is not None else lambda i: print(i))

    def read_multicast_table(self, callback=None):
        """
        - callback: call on each TableEntry
        """
        self.switch.TableEntry('MyEgress.switchfl_sender.switchfl_multicast_address').read(
            callback if callback is not None else lambda i: print(i))


def get_or_create_node(switch: p4sh,  node_id: int, bitmap: int, egress_port: int, egress_rid: int, mac: str, addr: str, rx_port: int, tx_port: int, switch_node, ps_node_id, role="", dryRun=False) -> Node:
    """
    role: 为 "ps" 时将会标记为参数服务器节点，"switch" 时将不会执行任何表操作，输入其他值暂时不做处理
    """
    if __node_cache_map.get(node_id) is None:
        __node_cache_map[node_id] = Node(
            switch=switch,
            node_id=node_id,
            bitmap=bitmap,
            egress_port=egress_port,
            egress_rid=egress_rid,
            mac=mac,
            addr=addr,
            rx_port=rx_port,
            tx_port=tx_port,
            switch_node=switch_node,
            ps_node_id=ps_node_id,
            role=role,
            dryRun=dryRun
        )
        __node_cache_map[node_id].apply()
    return __node_cache_map[node_id]
