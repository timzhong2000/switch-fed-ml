#ifndef SWITCH_FED_ML_TYPE_H
#define SWITCH_FED_ML_TYPE_H

#include <cstdint>

#define DATA_LEN 1024 // 一个包可以承载的字节数

namespace switchml
{
  typedef uint32_t TensorId;

  enum DataType
  {
    INT32,
    FLOAT32
  };

  struct SwitchmlHeader
  {

    TensorId tensor_id;

    /** 偏移量，代表偏移多少个 element，不是 byte，element 大小由 data_type 决定 */
    uint32_t offset;

    /** 多播组号，下发时此参数有效，默认为 0 代表不进行多播，这个参数可以用来判断是下发包还是聚合包 */
    uint16_t ucast_grp;
    uint16_t aggregate_num;

    bool ecn;
    bool bypass;
    DataType data_type;
    // TODO: 对齐
  };
}

#endif