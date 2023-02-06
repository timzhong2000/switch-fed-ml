// !!!
// 令聚合器聚合完成的那一个包，既要完整发给 ps 又要向 client 发送 ack，所以这里使用 PRE 实现包扩增
// 
// 约定 egress_rid == 1000 用于聚合完成后，构建向 client 发送 ack 的包

control Sender(
  inout headers_t hdr,
  inout metadata_t meta,
  inout standard_metadata_t standard_meta
)
{
  action set_dest(
    // ip
    IPv4Address src_addr,
    IPv4Address dst_addr,
    // udp
    bit<16> dst_port, 
    bit<16> src_port 
  ) {
    hdr.ipv4.src_addr = src_addr;
    hdr.ipv4.dst_addr = dst_addr;
    hdr.udp.src_port = src_port;
    hdr.udp.dst_port = dst_port;
  }

  action send_back() {
    IPv4Address temp_addr = hdr.ipv4.dst_addr;
    hdr.ipv4.dst_addr = hdr.ipv4.src_addr;
    hdr.ipv4.src_addr = temp_addr;

    bit<16> temp_port = hdr.udp.dst_port;
    hdr.udp.dst_port = hdr.udp.src_port;
    hdr.udp.src_port = temp_port;
  }

  action send_back_ack() {
    hdr.switchfl.ack = 1;
    send_back();
  }

  action send_back_ecn() {
    hdr.switchfl.ecn = 1;
    send_back();
  }

  // <egress_rid, tensor_id> 唯一确认了一个包的目的地
  table egress_rid_to_worker_address {
    key = {
      standard_meta.egress_rid: exact; // replication id
      hdr.switchfl.tensor_id: exact;
    }
    actions = {
      set_dest;
    }
  }

  apply {
    // send to ps and ack
    if(meta.processor_action == Processor_Action.MCAST) {
      if(standard_meta.egress_rid == 1000) {
        send_back_ack();
      } else {
        egress_rid_to_worker_address.apply();
      }
    }
    // ecn
    if(meta.processor_action == Processor_Action.ECN) {
      send_back_ecn();
    }
    if(meta.processor_action == Processor_Action.DROP) {
      mark_to_drop(standard_meta);
    }
  }
}