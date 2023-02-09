#ifndef _SWITCH_FL_TYPE
#define _SWITCH_FL_TYPE

typedef bit<48> EthernetAddress;
typedef bit<32> IPv4Address;
typedef bit<16> MulticastGroupId_t;
typedef bit<32> TensorId_t;
typedef bit<32> SegmentId_t;
typedef bit<32> Data_t;
typedef bit<16> PoolId_t;
typedef bit<32> WorkerBitmap_t;
typedef bit<16> AggregateNum_t; // 聚合数
typedef bit<16> NodeId_t;

const bit<16> SwitchFL_PORT = 50000;


enum bit<8> Processor_Action {
  ECN = 1,
  DROP = 2,
  MCAST = 3, // 下发模型
  ACK = 4, // 单播 ack
  FINISH = 5 // 聚合器释放时发送给 ps 并且广播 ack
}

struct metadata_t {
  
  ///           ingress               ///

  // 用于忽略重传包
  WorkerBitmap_t bitmap;
  
  // 当前组号的数据，总共需要聚合次数
  AggregateNum_t total_aggregate_num;

  // 聚合完成时的 bitmap，用于比对聚合结果
  bit<32> aggregate_finish_bitmap;

  // process 判断包发送行为
  Processor_Action processor_action;

  ///              egress              ///
  bool is_ps; 
}

header ethernet_h {
    EthernetAddress dst_addr;
    EthernetAddress src_addr;
    bit<16>         ether_type;
}

header ipv4_h {
    bit<4>      version;
    bit<4>      ihl;
    bit<8>      diffserv;
    bit<16>     total_len;
    bit<16>     identification;
    bit<3>      flags;
    bit<13>     frag_offset;
    bit<8>      ttl;
    bit<8>      protocol;
    bit<16>     hdr_checksum;
    IPv4Address src_addr;
    IPv4Address dst_addr;
}

header udp_h {
    bit<16> src_port;
    bit<16> dst_port;
    bit<16> length;
    bit<16> checksum;
}

// switch fl header
header switchfl_h {
  // 8bit
  // flow control start
  bit<1>              ack;
  bit<1>              ecn;
  bit<1>              bypass;
  bit<1>              multicast; // PS 向 client 发送的广播包
  bit<1>              retranmission; // client 重传包
  bit<3>              __reserved;
  // flow control end

  bit<8>              data_type;
  TensorId_t          tensor_id;      // 32bit
  SegmentId_t         segment_id;     // 32bit
  NodeId_t            node_id;
  AggregateNum_t      aggregate_num;  // 16bit
  MulticastGroupId_t  mcast_grp;      // 16bit
  PoolId_t            pool_id;        // 16bit
}

// switch fl payload
// 32 * uint32
// 单 switchfl 包包含多个 tensor_t
// 单个 tensor_t 长度 128 bytes 
header tensor_t {
  Data_t d0;
  Data_t d1;
  Data_t d2;
  Data_t d3;
  Data_t d4;
  Data_t d5;
  Data_t d6;
  Data_t d7;
  Data_t d8;
  Data_t d9;
  Data_t d10;
  Data_t d11;
  Data_t d12;
  Data_t d13;
  Data_t d14;
  Data_t d15;
  Data_t d16;
  Data_t d17;
  Data_t d18;
  Data_t d19;
  Data_t d20;
  Data_t d21;
  Data_t d22;
  Data_t d23;
  Data_t d24;
  Data_t d25;
  Data_t d26;
  Data_t d27;
  Data_t d28;
  Data_t d29;
  Data_t d30;
  Data_t d31;
}

struct headers_t {
  ethernet_h    ethernet;
  ipv4_h        ipv4;
  udp_h         udp;
  switchfl_h    switchfl;
  tensor_t      tensor0;
  tensor_t      tensor1;
  tensor_t      tensor2;
  tensor_t      tensor3;
  tensor_t      tensor4;
  tensor_t      tensor5;
  tensor_t      tensor6;
  tensor_t      tensor7;
}

#endif