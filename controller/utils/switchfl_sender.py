import p4runtime_sh.shell as p4sh
import typing

# reduce address: 在 reduce 阶段使用的 tuple(egress_port, egress_rid) => 用于重写的 udp 地址和 switch_node_id
# multicast address: 在 multicast 阶段使用的 tuple(egress_port, egress_rid) => 用于重写的 udp 地址和 ps_node_id


class Sender():
    def __init__(self, switch: p4sh, switch_node_id: int):
        self.switch = switch
        """
        保存当前已经添加过的节点，如果重复添加，会先执行删除再添加
        """
        self.__current_state = {}
        self.ps_node_id: typing.Optional[int] = None
        self.switch_node_id = switch_node_id

    def reset(self):
        for node_id in self.__current_state.keys():
            self.delete_node(node_id)

    # 其中 switch_addr 和 switch_port 用来支持一个 switch 连接到多个不同子网的情况

    def add_node(self, node_id: int, egress_port: int, egress_rid: int, switch_addr: int, switch_port: int, node_address: int, rx_port: int, tx_port: int, ps_node_id: int, is_ps: bool):
        if node_id in self.__current_state:
            self.delete_node(node_id)
        self.__current_state[node_id] = (egress_port, egress_rid)
        if is_ps:
            self.ps_node_id = node_id
            self.__insert_ps_mark(egress_port=egress_port,
                                  egress_rid=egress_rid)
        self.__insert_multicast_address(
            egress_port=egress_port,
            egress_rid=egress_rid,
            switch_addr=switch_addr,
            switch_port=switch_port,
            dst_addr=node_address,
            dst_port=rx_port,
            ps_node_id=ps_node_id,
        )
        self.__insert_reduce_address(
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
        te = self.switch.TableEntry('MyEgress.switchfl_sender.ps_mark')
        te.match['standard_meta.egress_port'] = "%d" % (egress_port)
        te.match['standard_meta.egress_rid'] = "%d" % (egress_rid)
        te.action['set_is_ps'] = ''
        te.insert()

    def __delete_ps_mark(self, egress_port: int, egress_rid: int):
        te = self.switch.TableEntry('MyEgress.switchfl_sender.ps_mark')
        te.match['standard_meta.egress_port'] = "%d" % (egress_port)
        te.match['standard_meta.egress_rid'] = "%d" % (egress_rid)
        te.delete()

    def __insert_reduce_address(self, egress_port: int, egress_rid: int, switch_addr: int, dst_addr: int, switch_port: int, dst_port: int, switch_node_id: int):
        te = self.switch.TableEntry(
            'MyEgress.switchfl_sender.switchfl_reduce_address')
        te.match['standard_meta.egress_port'] = "%d" % (egress_port)
        te.match['standard_meta.egress_port'] = "%d" % (egress_rid)
        te.action['set_dest'] = "%d, %d, %d, %d, %d" % (
            switch_addr, dst_addr, switch_port, dst_port, switch_node_id)
        te.insert()

    def __delete_reduce_address(self, egress_port: int, egress_rid: int):
        te = self.switch.TableEntry(
            'MyEgress.switchfl_sender.switchfl_reduce_address')
        te.match['standard_meta.egress_port'] = "%d" % (egress_port)
        te.match['standard_meta.egress_port'] = "%d" % (egress_rid)
        te.delete()

    def __insert_multicast_address(self, egress_port: int, egress_rid: int, switch_addr: int, dst_addr: int, switch_port: int, dst_port: int, ps_node_id: int):
        # 广播地址
        te = self.switch.TableEntry(
            'MyEgress.switchfl_sender.switchfl_multicast_address')
        te.match['standard_meta.egress_port'] = "%d" % (egress_port)
        te.match['standard_meta.egress_port'] = "%d" % (egress_rid)
        te.action['set_dest'] = "%d, %d, %d, %d, %d" % (
            switch_addr, dst_addr, switch_port, dst_port, ps_node_id)
        te.insert()

    def __delete_multicast_address(self, egress_port: int, egress_rid: int):
        # 广播地址
        te = self.switch.TableEntry(
            'MyEgress.switchfl_sender.switchfl_multicast_address')
        te.match['standard_meta.egress_port'] = "%d" % (egress_port)
        te.match['standard_meta.egress_port'] = "%d" % (egress_rid)
        te.delete()
