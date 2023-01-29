#ifndef SWITCH_FED_ML_BITMAP_H
#define SWITCH_FED_ML_BITMAP_H

#include <cstddef>
#include <vector>

namespace switchml
{
  class Bitmap
  {
  public:
    Bitmap(size_t size);
    void set(size_t index, bool val);
    bool get(size_t index);

  private:
    std::vector<bool> bitmap;
  };
}
#endif