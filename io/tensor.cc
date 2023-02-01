#include "tensor.h"
#include <cstdlib>
#include <cstring>

namespace switchfl
{
  Tensor::Tensor(uint64_t len, uint8_t data_type, TensorId tensor_id) : len(len), data_type(data_type), tensor_id(tensor_id), aggregate_num(1)
  {
    this->buffer = malloc(sizeofDataType(data_type) * len);
  }

  Tensor::Tensor(void *buffer, uint64_t len, uint8_t data_type, TensorId tensor_id) : buffer(buffer), len(len), data_type(data_type), tensor_id(tensor_id), is_external_buffer(true), aggregate_num(1)
  {
  }

  Tensor::Tensor(Tensor &&tensor)
  {
    this->buffer = tensor.buffer;
    this->data_type = tensor.data_type;
    this->len = tensor.len;
    this->tensor_id = tensor.tensor_id;
    this->aggregate_num = tensor.aggregate_num;
    tensor.buffer = nullptr;
    tensor.len = 0;
    tensor.tensor_id = 0;
  }

  Tensor::~Tensor()
  {
    if (this->buffer && !this->is_external_buffer)
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

  void Tensor::add(Tensor &tensor)
  {
    if (this->data_type == INT32_TYPE) 
    {
      auto d1 = static_cast<int *>(this->buffer);
      auto d2 = static_cast<int *>(tensor.buffer);
      for (size_t i = 0; i < this->len; i++)
      {
        d1[i] += d2[i];
      }
    }
    else if (this->data_type == FLOAT32_TYPE)
    {
      auto d1 = static_cast<float *>(this->buffer);
      auto d2 = static_cast<float *>(tensor.buffer);
      for (size_t i = 0; i < this->len; i++)
      {
        d1[i] += d2[i];
      }
    }
  }

  void Tensor::divide(int factor)
  {
    if (this->data_type == INT32_TYPE)
    {
      auto d1 = static_cast<int *>(this->buffer);
      for (size_t i = 0; i < this->len; i++)
      {
        d1[i] /= factor;
      }
    }
    else if (this->data_type == FLOAT32_TYPE)
    {
      auto d1 = static_cast<float *>(this->buffer);
      for (size_t i = 0; i < this->len; i++)
      {
        d1[i] /= factor;
      }
    }
  }

  void *Tensor::seek(uint64_t offset)
  {
    return (uint8_t *)this->buffer + sizeofDataType(this->data_type) * offset;
  }
}
