from scapy.all import *
from packet import *
import numpy as np

pkt = Packet()
pkt.set_header(
  flow_control=0,
  data_type=0,
  tensor_id=100,
  segment_id=0,
  node_id=2,
  aggregate_num=1,
  mcast_grp=2,
  pool_id=0
)
pkt.set_tensor(np.ones((256), dtype=np.int32))
pkt.deparse_header()
pkt.deparse_payload()
p = Ether()/IP(src="11.11.11.1", dst="11.11.1.3")/UDP(dport=50000)/str(pkt.buffer, encoding="utf8")
sendp(p, iface="veth1")

time.sleep(1)

pkt = Packet()
pkt.set_header(
  flow_control=0,
  data_type=0,
  tensor_id=100,
  segment_id=0,
  node_id=1,
  aggregate_num=1,
  mcast_grp=2,
  pool_id=0
)
pkt.set_tensor(np.ones((256), dtype=np.int32))
pkt.deparse_header()
pkt.deparse_payload()
p = Ether()/IP(src="11.11.11.1", dst="11.11.1.3")/UDP(dport=50000)/str(pkt.buffer, encoding="utf8")
sendp(p, iface="veth1")
