import p4runtime_sh.shell as p4sh

class Receiver():
    def __init__(self, switch: p4sh, dryRun: bool = False):
        self.switch = switch
        # mcast_grp => dict[node_id, (bitmap, egress_port, egress_rid)]]
        self.__current_state = {}
        # mcast_grp => (node_id, egress_port, egress_rid)
        self.__ps_state = {}
        self.__dryRun = dryRun

    def reset(self):
        for mcast_grp in self.__current_state.keys():
            self.__delete_group(mcast_grp)

    def init_group(self, ps_node_id: int, mcast_grp: int, egress_port: int, egress_rid: int):
        self.__ps_state[mcast_grp] = (ps_node_id, egress_port, egress_rid)
        self.__current_state[mcast_grp] = {}
        self.__apply_group(mcast_grp)

    def add_worker_to_group(self, node_id: int, mcast_grp: int, egress_port: int, egress_rid: int, node_bitmap: int):
        if self.__current_state.get(mcast_grp) is None:
            raise "please init_group before adding worker"
        self.__reset_group(mcast_grp)
        self.__current_state[mcast_grp][node_id] = (
            node_bitmap, egress_port, egress_rid)
        self.__apply_group(mcast_grp)

    def delete_worker_from_group(self, node_id: int, mcast_grp: int):
        if self.__current_state[mcast_grp].get(node_id) is None:
            return
        del self.__current_state[mcast_grp][node_id]
        if len(self.__current_state[mcast_grp]) == 0:
            self.__delete_group(mcast_grp)

    def __apply_group(self, mcast_grp: int):
        # init
        aggregate_finish_bitmap = 0
        total_aggregate_num = len(self.__current_state[mcast_grp])
        replicas = []
        for node_id, (bitmap, egress_port, egress_rid) in self.__current_state[mcast_grp].items():
            aggregate_finish_bitmap |= bitmap
            replicas.append({"egress_port": egress_port,
                            "egress_rid": egress_rid})
        # apply
        self.__insert_group_config(
            mcast_grp, total_aggregate_num, aggregate_finish_bitmap)
        self.__insert_mcast_replicas(mcast_grp, replicas)
        for node_id, (bitmap, _, _) in self.__current_state[mcast_grp].items():
            self.__insert_worker_bitmap(node_id, bitmap)

    def __reset_group(self, mcast_grp: int):
        self.__delete_group_config(mcast_grp)
        self.__delete_mcast_replicas(mcast_grp)
        for node_id in self.__current_state[mcast_grp].keys():
            self.__delete_worker_bitmap(node_id)

    def __delete_group(self, mcast_grp: int):
        self.__reset_group(mcast_grp)
        del self.__current_state[mcast_grp]
        del self.__ps_state[mcast_grp]

    # 从 header.node_id 到聚合器识别的 node bitmap 的映射
    def __insert_worker_bitmap(self, node_id: int, node_bitmap: int):
        if self.__dryRun:
            print("[Receiver Controller] __insert_worker_bitmap node_id=%d, node_bitmap=%d" % (
                node_id, node_bitmap))
            return
        te = self._get_worker_bitmap_table_entry(node_id)(action='set_bitmap')
        te.action.set(bitmap=str(node_bitmap))
        te.insert()

    def __delete_worker_bitmap(self, node_id: int):
        if self.__dryRun:
            print("[Receiver Controller] __delete_worker_bitmap node_id=%d" % (node_id))
            return
        self._get_worker_bitmap_table_entry(node_id).delete()

    # 从 header.mcast_grp 到聚合器识别的 aggregate_finish_bitmap 的映射
    def __insert_group_config(self, mcast_grp: int, total_aggregate_num: int, aggregate_finish_bitmap: int):
        if self.__dryRun:
            print("[Receiver Controller] __insert_group_config mcast_grp=%d, total_aggregate_num=%d, aggregate_finish_bitmap=%d" % (
                mcast_grp, total_aggregate_num, aggregate_finish_bitmap))
            return
        te = self._get_group_config_table_entry(mcast_grp)(action='set_group_config')
        te.action.set(total_aggregate_num=str(total_aggregate_num),
                      aggregate_finish_bitmap=str(aggregate_finish_bitmap))
        te.insert()

    def __delete_group_config(self, mcast_grp: int):
        if self.__dryRun:
            print(
                "[Receiver Controller] __delete_group_config mcast_grp=%d" % (mcast_grp))
            return
        self._get_group_config_table_entry(mcast_grp).delete()

    # PacketReplicationEngine 表
    def __insert_mcast_replicas(self, mcast_grp: int, replicas: list):
        if self.__dryRun:
            print(
                "[Receiver Controller] __insert_mcast_replicas mcast_grp=%d" % (mcast_grp))
            print(replicas)
            return
        mcge = self.switch.MulticastGroupEntry(mcast_grp)
        for replica in replicas:
            mcge.add(replica['egress_port'], replica['egress_rid'])
        mcge.insert()

    def __delete_mcast_replicas(self, mcast_grp: int):
        if self.__dryRun:
            print(
                "[Receiver Controller] __delete_mcast_replicas mcast_grp=%d" % (mcast_grp))
            return
        mcge = self.switch.MulticastGroupEntry(mcast_grp)
        mcge.delete()

    def _get_group_config_table_entry(self, mcast_grp: int):
        te = self.switch.TableEntry('MyIngress.switchfl_receiver.group_config')
        te.match['hdr.switchfl.mcast_grp'] = str(mcast_grp)
        return te

    def _get_worker_bitmap_table_entry(self, node_id: int):
        te = self.switch.TableEntry('MyIngress.switchfl_receiver.worker_bitmap')
        te.match['hdr.switchfl.node_id'] = str(node_id)
        return te
