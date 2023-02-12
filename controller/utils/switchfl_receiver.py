import p4runtime_sh.shell as p4sh


class Receiver():
    def __init__(self, switch: p4sh):
        self.switch = switch
        self.__current_state = {}  # node_id => mcast_grp

    def reset(self):
        for node_id in self.__current_state.keys():
            self.delete_node(node_id)

    def add_node(self, node_id: int, mcast_grp: int, node_bitmap: int, total_aggregate_num: int, aggregate_finish_bitmap: int):
        if node_id in self.__current_state:
            self.delete_node(node_id)
        self.__current_state[node_id] = mcast_grp
        self.__insert_group_config(mcast_grp=mcast_grp, total_aggregate_num=total_aggregate_num,
                                   aggregate_finish_bitmap=aggregate_finish_bitmap)
        self.__insert_worker_bitmap(
            mcast_grp=mcast_grp, node_bitmap=node_bitmap)

    def delete_node(self, node_id):
        if node_id not in self.__current_state:
            raise "node_id %d not found" % (node_id)
        mcast_grp = self.__current_state[node_id]
        self.__delete_group_config(mcast_grp)
        self.__delete_worker_bitmap(mcast_grp)
        del self.__current_state[node_id]

    # 从 header.node_id 到聚合器识别的 node bitmap 的映射
    def __insert_worker_bitmap(self, node_id: int, node_bitmap: int):
        te = self.switch.TableEntry(
            'MyIngress.switchfl_receiver.worker_bitmap')
        te.match['hdr.switchfl.node_id'] = node_id
        te.action['set_bitmap'] = "%d" % (node_bitmap)
        te.insert()

    def __delete_worker_bitmap(self, node_id: int):
        te = self.switch.TableEntry(
            'MyIngress.switchfl_receiver.worker_bitmap')
        te.match['hdr.switchfl.node_id'] = node_id
        te.delete()

    def __insert_group_config(self, mcast_grp: int, total_aggregate_num: int, aggregate_finish_bitmap: int):
        te = self.switch.TableEntry('MyIngress.switchfl_receiver.group_config')
        te.match['hdr.switchfl.mcast_grp'] = mcast_grp
        te.action['set_group_config'] = "%d,%d" % (
            total_aggregate_num, aggregate_finish_bitmap)
        te.insert()

    def __delete_group_config(self, mcast_grp: int):
        te = self.switch.TableEntry('MyIngress.switchfl_receiver.group_config')
        te.match['hdr.switchfl.mcast_grp'] = mcast_grp
        te.delete()
