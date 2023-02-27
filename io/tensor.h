#pragma once

#include <cstdint>
#include "packet.h"
#include "type.h"

namespace switchfl
{

  class Tensor
  {
  public:
    void *buffer;
    uint64_t len; // the len of element, not byte
    uint8_t data_type;
    TensorId round_id;
    AggregateNum aggregate_num;

    /** create a new tensor*/
    Tensor(uint64_t len, uint8_t data_type, TensorId round_id);

    /**
     * @deprecated not recommend, the **external buffer** pointer is **dangerous**
     */
    Tensor(void *buffer, uint64_t len, uint8_t data_type, TensorId round_id);

    /** do not support tensor copy */
    Tensor(Tensor &tensor) = delete;

    /** support tensor move*/
    Tensor(Tensor &&tensor);

    ~Tensor();

    /**
     * copy buf to tensor.
     *
     * the element size is determined by data_type
     *
     * @param len number of element
     * @return -1 if tensor is moved, -2 if exceed max length;
     */
    int write(void *buf, uint64_t offset, uint64_t len);

    void add(Tensor &tensor);

    void divide(int factor);

    void *seek(uint64_t offset);

  private:
    bool is_external_buffer = false;
  };
}