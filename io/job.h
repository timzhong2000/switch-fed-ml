#pragma once

#include "tensor.h"
#include "packet.h"
#include "bitmap.h"
#include <memory>
#include <vector>
#include <mutex>

namespace switchfl
{
  class Job
  {
  public:
    Job(std::shared_ptr<Tensor> tensor, std::shared_ptr<Bitmap> bitmap);
    ~Job();

    void wait_until_job_finish();
    void handle_packet(const Packet &pkt);
    void finish();

    // private:
    std::shared_ptr<Tensor> tensor;
    std::shared_ptr<Bitmap> bitmap;
    std::mutex finish_lock;
  };
}
