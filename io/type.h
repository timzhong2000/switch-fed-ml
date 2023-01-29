#ifndef SWITCH_FED_ML_TYPE_H
#define SWITCH_FED_ML_TYPE_H

#include <cstdint>

#define DATA_LEN 1024 // 一个包可以承载的字节数

namespace switchml
{
  typedef uint32_t TensorId;
  typedef uint32_t Offset;
  typedef uint16_t NodeId;
  typedef uint8_t AggregateNum;

  enum DataType
  {
    INT32,
    FLOAT32
  };

  struct SwitchmlHeader
  {
    // 0 byte

    TensorId tensor_id;

    // 4 byte

    /** 偏移量，代表偏移多少个 element，不是 byte，element 大小由 data_type 决定 */
    Offset offset;

    // 8 byte

    /** 多播组号，下发时此参数有效，默认为 0 代表不进行多播，这个参数可以用来判断是下发包还是聚合包 */
    NodeId node_id;
    uint8_t ucast_grp;
    AggregateNum aggregate_num;

    // 96bit
    bool ecn;
    bool bypass;
    DataType data_type;
    // TODO: 对齐
  };
}

#endif