#pragma once

#include <cstddef>
#include <vector>

namespace switchfl
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