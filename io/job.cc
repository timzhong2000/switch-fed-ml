#include "job.h"
namespace switchfl
{
  Job::Job(std::shared_ptr<Tensor> tensor,std::shared_ptr<Bitmap> bitmap) 
  {
    this->bitmap = bitmap;
    this->tensor = tensor;
    this->finish_lock.lock();
  }

  Job::~Job() {}

  void Job::wait_until_job_finish()
  {
    this->finish_lock.lock();
    this->finish_lock.unlock();
  }

  void Job::handle_packet(const Packet &pkt)
  {
    auto elements_per_packet = (DATA_LEN / sizeofDataType(tensor->data_type));
    this->tensor->write(pkt.data, pkt.header->packet_id * elements_per_packet, elements_per_packet);
    this->bitmap->set(pkt.header->packet_id, true);
  }

  void Job::finish()
  {
    this->finish_lock.unlock();
  }
} // namespace switchfl
