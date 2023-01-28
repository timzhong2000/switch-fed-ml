#include "tensor.h"
#include <cstdlib>
#include <cstring>

namespace switchml
{
  Tensor::Tensor(uint64_t len, DataType data_type, TensorId tensor_id) : len(len), data_type(data_type), tensor_id(tensor_id)
  {
    this->buffer = malloc(sizeofDataType(data_type) * len);
  }

  Tensor::Tensor(Tensor &&tensor)
  {
    this->buffer = tensor.buffer;
    this->data_type = tensor.data_type;
    this->len = tensor.len;
    this->tensor_id = tensor.tensor_id;
    tensor.buffer = nullptr;
    tensor.len = 0;
    tensor.tensor_id = 0;
  }

  Tensor::~Tensor()
  {
    if (this->buffer)
    {
      free(this->buffer);
    }
  }

  int Tensor::write(void *buf, uint64_t offset, uint64_t len)
  {
    if (!this->buffer)
      return -1;
    if (this->len < offset + len)
      return -2;

    memcpy(this->seek(offset), buf, sizeofDataType(this->data_type) * len);
    return 0;
  }

  void *Tensor::seek(uint64_t offset)
  {
    return this->buffer + sizeofDataType(this->data_type) * offset;
  }
}
