import p4runtime_sh.shell as p4sh

class PacketReplicationEngine():
    def __init__(self, switch: p4sh):
        self.switch = switch
        self.__current_state = {}

    def reset(self):
        for mcast_grp in self.__current_state.keys():
            self.delete_mcast_grp(mcast_grp)

    def delete_mcast_grp(self, mcast_grp: int):
        del self.__current_state[mcast_grp]
        mcge = self.switch.MulticastGroupEntry(mcast_grp)
        mcge.delete()

    def add_mcast_replicas(self, mcast_grp: int, replicas: list):
        if mcast_grp in self.__current_state:
            self.delete_mcast_grp(mcast_grp)
        self.__current_state[mcast_grp] = replicas
        mcge = self.switch.MulticastGroupEntry(mcast_grp)
        for replica in replicas:
            mcge.add(replica['egress_port'], replica['egress_rid'])
        mcge.insert()