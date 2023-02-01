#pragma once

#include <cstdint>

#define DATA_LEN 1024 // 一个包可以承载的字节数
#define FLOAT32_TYPE 1
#define INT32_TYPE 0

namespace switchfl
{
  typedef uint32_t TensorId;
  typedef uint32_t PacketId;
  typedef uint16_t NodeId;
  typedef uint16_t AggregateNum;
  typedef uint32_t GroupId;

  struct SwitchmlHeader
  {
    // 0 byte

    uint8_t flow_control;
    uint8_t data_type;

    // 2 byte

    TensorId tensor_id;

    // 6 byte

    PacketId packet_id;

    // 10 byte
    NodeId node_id;
    AggregateNum aggregate_num;

    // 14 byte

    /** 多播组号，下发时此参数有效，默认为 0 代表不进行多播，这个参数可以用来判断是下发包还是聚合包 */
    GroupId ucast_grp;

    // 18 byte
  };
}
