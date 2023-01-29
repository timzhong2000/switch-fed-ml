#include "bitmap.h"

namespace switchml
{
  Bitmap::Bitmap(size_t size)
  {
    this->bitmap = new bool[size];
  }

  Bitmap::~Bitmap()
  {
    delete[] this->bitmap;
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