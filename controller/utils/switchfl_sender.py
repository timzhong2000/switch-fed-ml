import p4runtime_sh.shell as p4sh
import typing

# reduce address: 在 reduce 阶段使用的 tuple(egress_port, egress_rid) => 用于重写的 udp 地址和 switch_node_id
# multicast address: 在 multicast 阶段使用的 tuple(egress_port, egress_rid) => 用于重写的 udp 地址和 ps_node_id


class Sender():
    def __init__(self, switch: p4sh, switch_node_id: int, switch_mac: str, dryRun: bool = False):
        self.switch = switch
        """
        保存当前已经添加过的节点，如果重复添加，会先执行删除再添加
        """
        self.__current_state = {}
        self.ps_node_id: typing.Optional[int] = None
        self.switch_node_id = switch_node_id
        self.switch_mac = switch_mac
        self.__dryRun = dryRun

    def reset(self):
        for node_id in self.__current_state.keys():
            self.delete_node(node_id)

    # 其中 switch_addr 和 switch_port 用来支持一个 switch 连接到多个不同子网的情况

    def add_node(self, node_id: int, node_mac: str, egress_port: int, egress_rid: int, switch_addr: str, switch_port: str, node_address: str, rx_port: int, tx_port: int, ps_node_id: int, is_ps: bool):
        if node_id in self.__current_state:
            self.delete_node(node_id)
        self.__current_state[node_id] = (egress_port, egress_rid)
        if is_ps:
            self.ps_node_id = node_id
            self.__insert_ps_mark(egress_port=egress_port,
                                  egress_rid=egress_rid)
        self.__insert_multicast_address(
            dst_mac=node_mac,
            egress_port=egress_port,
            egress_rid=egress_rid,
            switch_addr=switch_addr,
            switch_port=switch_port,
            dst_addr=node_address,
            dst_port=rx_port,
            ps_node_id=ps_node_id,
        )
        self.__insert_reduce_address(
            dst_mac=node_mac,
            egress_port=egress_port,
            egress_rid=egress_rid,
            switch_addr=switch_addr,
            switch_port=switch_port,
            dst_addr=node_address,
            dst_port=tx_port,
            switch_node_id=self.switch_node_id
        )

    def delete_node(self, node_id: int):
        if node_id not in self.__current_state:
            raise "node_id %d not exist"
        egress_port, egress_rid = self.__current_state[node_id]
        if node_id == self.ps_node_id:
            self.__delete_ps_mark(egress_port, egress_rid)
        self.__delete_multicast_address(egress_port, egress_rid)
        self.__delete_reduce_address(egress_port, egress_rid)
        del self.__current_state[node_id]

    def __insert_ps_mark(self, egress_port: int, egress_rid: int):
        if self.__dryRun:
            return
        te = self._get_ps_mark_table_entry(
            egress_port, egress_rid)(action='set_is_ps')
        te.insert()

    def __delete_ps_mark(self, egress_port: int, egress_rid: int):
        if self.__dryRun:
            return
        self._get_ps_mark_table_entry(egress_port, egress_rid).delete()

    def __insert_reduce_address(self, egress_port: int, egress_rid: int, dst_mac: str, switch_addr: str, dst_addr: str, switch_port: int, dst_port: int, switch_node_id: int):
        if self.__dryRun:
            print("[Sender Controller] __insert_reduce_address [egress_port=%d, egress_rid=%d] => src=%s:%d (%s), dst=%s:%d (%s), rewrite_node_id=%d" % (
                egress_port, egress_rid, switch_addr, switch_port, self.switch_mac, dst_addr, dst_port, dst_mac, switch_node_id))
            return
        te = self._get_reduce_table_entry(
            egress_port, egress_rid)(action='set_dest')
        te.action.set(
            src_mac=self.switch_mac,
            dst_mac=dst_mac,
            src_addr=switch_addr,
            src_port=str(switch_port),
            dst_addr=dst_addr,
            dst_port=str(dst_port),
            node_id=str(switch_node_id)
        )
        te.insert()

    def __delete_reduce_address(self, egress_port: int, egress_rid: int):
        if self.__dryRun:
            print("[Sender Controller] __delete_reduce_address [egress_port=%d, egress_rid=%d]" % (
                egress_port, egress_rid))
            return
        self._get_reduce_table_entry(egress_port, egress_rid).delete()

    def __insert_multicast_address(self, egress_port: int, egress_rid: int, dst_mac: str, switch_addr: str, dst_addr: str, switch_port: str, dst_port: int, ps_node_id: int):
        if self.__dryRun:
            print("[Sender Controller] __insert_multicast_address [egress_port=%d, egress_rid=%d] => src=%s:%d (%s), dst=%s:%d (%s), rewrite_node_id=%d" % (
                egress_port, egress_rid, switch_addr, switch_port, self.switch_mac, dst_addr, dst_port, dst_mac, ps_node_id))
            return
        te = self._get_multicast_table_entry(
            egress_port, egress_rid)(action='set_dest')
        te.action.set(
            src_mac=self.switch_mac,
            dst_mac=dst_mac,
            src_addr=switch_addr,
            dst_addr=dst_addr,
            src_port=str(switch_port),
            dst_port=str(dst_port),
            node_id=str(ps_node_id)
        )
        te.insert()

    def __delete_multicast_address(self, egress_port: int, egress_rid: int):
        if self.__dryRun:
            print("[Sender Controller] __delete_multicast_address [egress_port=%d, egress_rid=%d]" % (
                egress_port, egress_rid))
            return
        self._get_multicast_table_entry(egress_port, egress_rid).delete()

    def _get_ps_mark_table_entry(self, egress_port: int, egress_rid: int):
        te = self.switch.TableEntry('MyEgress.switchfl_sender.ps_mark')
        self.__set_table_match(te, egress_port, egress_rid)
        return te

    def _get_reduce_table_entry(self, egress_port: int, egress_rid: int):
        te = self.switch.TableEntry(
            'MyEgress.switchfl_sender.switchfl_reduce_address')
        self.__set_table_match(te, egress_port, egress_rid)
        return te

    def _get_multicast_table_entry(self, egress_port: int, egress_rid: int):
        te = self.switch.TableEntry(
            'MyEgress.switchfl_sender.switchfl_multicast_address')
        self.__set_table_match(te, egress_port, egress_rid)
        return te

    def __set_table_match(self, te: p4sh.TableEntry, egress_port: int, egress_rid: int):
        te.match['standard_meta.egress_port'] = str(egress_port)
        te.match['standard_meta.egress_rid'] = str(egress_rid)

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
