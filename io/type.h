#ifndef SWITCH_FED_ML_TYPE_H
#define SWITCH_FED_ML_TYPE_H

#include <cstdint>

#define DATA_LEN 1024

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