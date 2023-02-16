import p4runtime_sh.shell as p4sh
import pandas

class RouteTable():
    def __init__(self, switch: p4sh, dryRun=False) -> None:
        self.switch = switch
        self.route_table = {}  # subnet => egress_port
        self.__dryRun = dryRun

    def add_rule(self, subnet: str, egress_port: int):
        if self.route_table.get(subnet) is not None:
            raise "subnet %s exist, please modify or delete it" % (subnet)
        if not self.__dryRun:
            te = self.__get_ipv4_match_table_entry(
                subnet)(action='to_port_action')
            te.action.set(port=str(egress_port))
            te.insert()
        self.route_table[subnet] = egress_port

    def modify_rule(self, subnet: str, egress_port: int):
        if self.route_table.get(subnet) is None:
            raise "subnet %s not found, please add_rule before modifing" % (
                subnet)
        if not self.__dryRun:
            te = self.__get_ipv4_match_table_entry(
                subnet)(action='to_port_action')
            te.action.set(port=str(egress_port))
            te.modify()
        self.route_table[subnet] = egress_port

    def delete_rule(self, subnet: str):
        if self.route_table.get(subnet) is None:
            raise "subnet %s not found, please add_rule before deleting" % (
                subnet)
        if not self.__dryRun:
            self.__get_ipv4_match_table_entry(subnet).delete()
        del self.route_table[subnet]

    def __get_ipv4_match_table_entry(self, subnet: str):
        te = self.switch.TableEntry("MyIngress.ipv4_match")
        te.match['hdr.ipv4.dst_addr'] = subnet
        return te

    def print_route_table(self):
        headers = ["dst_addr", "to_port"]
        data = [[subnet, egress_port] for subnet, egress_port in self.route_table.items()]
        print(pandas.DataFrame(data, None, headers))

if __name__ == "__main__":
    route_table = RouteTable(switch=None, dryRun=True)
    route_table.add_rule("192.168.1.0/24", 1)
    route_table.add_rule("192.168.2.0/24", 2)
    route_table.add_rule("10.10.0.0/16", 3)
    route_table.print_route_table()
