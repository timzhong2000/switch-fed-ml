#ifndef SWITCH_FED_ML_TENSOR_H
#define SWITCH_FED_ML_TENSOR_H

#include <cstdint>
#include "packet.h"

namespace switchml
{
  class Tensor
  {
    void *buffer;
    uint64_t len;
    DataType data_type;

    /** create a new tensor*/
    Tensor(uint64_t len, DataType data_type);

    /**
     * create a tensor slice, the element size is defined by data_type
     * @param offset offset of element
     * @param len len of element
     */
    Tensor(Tensor tensor, uint64_t offset, uint64_t len);

    /** do not support tensor copy */
    Tensor(Tensor &tensor) = delete;

    /** support tensor move*/
    Tensor(Tensor &&tensor);

    ~Tensor();
  };
}
#endif