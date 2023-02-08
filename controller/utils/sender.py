import p4runtime_sh.shell as sh

def insert_reduce_address(egress_port: int, egress_rid: int, switch_addr: int, dst_addr: int, switch_port: int, dst_port: int, switch_node_id: int):
    # 聚合地址
    te = sh.TableEntry('MyEgress.switchfl_sender.switchfl_reduce_address')
    te.match['standard_meta.egress_port'] = "%d" % (egress_port)
    te.match['standard_meta.egress_port'] = "%d" % (egress_rid)
    te.action['set_dest'] = "%d, %d, %d, %d, %d" % (switch_addr, dst_addr, switch_port, dst_port, switch_node_id)
    te.insert()

def delete_reduce_address(egress_port: int, egress_rid: int):
    # 聚合地址
    te = sh.TableEntry('MyEgress.switchfl_sender.switchfl_reduce_address')
    te.match['standard_meta.egress_port'] = "%d" % (egress_port)
    te.match['standard_meta.egress_port'] = "%d" % (egress_rid)
    te.delete()

def insert_multicast_address(egress_port: int, egress_rid: int, switch_addr: int, dst_addr: int, switch_port: int, dst_port: int, ps_node_id: int):
    # 广播地址
    te = sh.TableEntry('MyEgress.switchfl_sender.switchfl_multicast_address')
    te.match['standard_meta.egress_port'] = "%d" % (egress_port)
    te.match['standard_meta.egress_port'] = "%d" % (egress_rid)
    te.action['set_dest'] = "%d, %d, %d, %d, %d" % (switch_addr, dst_addr, switch_port, dst_port, ps_node_id)
    te.insert()

def delete_multicast_address(egress_port: int, egress_rid: int):
    # 广播地址
    te = sh.TableEntry('MyEgress.switchfl_sender.switchfl_multicast_address')
    te.match['standard_meta.egress_port'] = "%d" % (egress_port)
    te.match['standard_meta.egress_port'] = "%d" % (egress_rid)
    te.delete()

def insert_ps_mark(egress_port: int, egress_rid: int):
    # PS 标记
    te = sh.TableEntry('MyEgress.switchfl_sender.ps_mark')
    te.match['standard_meta.egress_port'] = "%d" % (egress_port)
    te.match['standard_meta.egress_rid'] = "%d" % (egress_rid)
    te.action['set_is_ps'] = ''
    te.insert()

def delete_ps_mark(egress_port: int, egress_rid: int):
    # PS 标记
    te = sh.TableEntry('MyEgress.switchfl_sender.ps_mark')
    te.match['standard_meta.egress_port'] = "%d" % (egress_port)
    te.match['standard_meta.egress_rid'] = "%d" % (egress_rid)
    te.delete()