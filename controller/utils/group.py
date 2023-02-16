import p4runtime_sh.shell as p4sh

__group_cache_map = {}  # Map<mcast_grp, Group>


class Group():
    def __init__(self, switch: p4sh, mcast_grp: int, ps_node, dryRun=False) -> None:
        self.switch = switch
        self.mcast_grp = mcast_grp
        self.ps_node = ps_node
        self.node_map = {}
        self.__dryRun = dryRun
        self.apply()

    def delete(self):
        self.reset()
        del __group_cache_map[self.mcast_grp]
        for node in self.node_map.values():
            node.unlink_to_group(self)

    def reset(self):
        self.__delete_mcast_replicas()
        self.__delete_group_config()

    def apply(self):
        aggregate_finish_bitmap = 0
        total_aggregate_num = len(self.node_map)
        replicas = [self.ps_node]
        for node in self.node_map.values():
            aggregate_finish_bitmap |= node.bitmap
            replicas.append(node)
        self.__insert_group_config(
            total_aggregate_num, aggregate_finish_bitmap)
        self.__insert_mcast_replicas(replicas)

    def _get_group_config_table_entry(self):
        te = self.switch.TableEntry('MyIngress.switchfl_receiver.group_config')
        te.match['hdr.switchfl.mcast_grp'] = str(self.mcast_grp)
        return te

    # 从 header.mcast_grp 到聚合器识别的 aggregate_finish_bitmap 的映射
    def __insert_group_config(self, total_aggregate_num: int, aggregate_finish_bitmap: int):
        if self.__dryRun:
            print("[Group Controller] __insert_group_config mcast_grp=%d, total_aggregate_num=%d, aggregate_finish_bitmap=%d" % (
                self.mcast_grp, total_aggregate_num, aggregate_finish_bitmap))
            return
        te = self._get_group_config_table_entry()(action='set_group_config')
        te.action.set(total_aggregate_num=str(total_aggregate_num),
                      aggregate_finish_bitmap=str(aggregate_finish_bitmap))
        te.insert()

    def __delete_group_config(self):
        if self.__dryRun:
            print(
                "[Group Controller] __delete_group_config mcast_grp=%d" % (self.mcast_grp))
            return
        self._get_group_config_table_entry().delete()

    # PacketReplicationEngine 表
    def __insert_mcast_replicas(self, replicas: list):
        if self.__dryRun:
            print(
                "[Group Controller] __insert_mcast_replicas mcast_grp=%d" % (self.mcast_grp))
            print(replicas)
            return
        mcge = self.switch.MulticastGroupEntry(self.mcast_grp)
        for node in replicas:
            mcge.add(node.egress_port, node.egress_rid)
        mcge.insert()

    def __delete_mcast_replicas(self):
        if self.__dryRun:
            print(
                "[Group Controller] __delete_mcast_replicas mcast_grp=%d" % (self.mcast_grp))
            return
        mcge = self.switch.MulticastGroupEntry(self.mcast_grp)
        mcge.delete()


def get_or_create_group(switch: p4sh, mcast_grp: int, ps_node):
    if __group_cache_map.get(mcast_grp) is None:
        __group_cache_map[mcast_grp] = Group(switch, mcast_grp, ps_node)
    return __group_cache_map[mcast_grp]
