#ifndef SWITCH_FED_ML_BITMAP_H
#define SWITCH_FED_ML_BITMAP_H

#include <cstddef>

namespace switchml
{
  class Bitmap
  {
  public:
    Bitmap(size_t size);
    ~Bitmap();
    void set(size_t index, bool val);
    bool get(size_t index);

  private:
    bool *bitmap;
  };
}
#endif