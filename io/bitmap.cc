#include "bitmap.h"

namespace switchml
{
  Bitmap::Bitmap(size_t size)
  {
    this->bitmap.reserve(size);
    for (size_t i = 0; i < size; i++)
    {
      bitmap.push_back(false);
    }
  }

  void Bitmap::set(size_t index, bool val)
  {
    this->bitmap[index] = val;
  }

  bool Bitmap::get(size_t index)
  {
    return this->bitmap[index];
  }
}