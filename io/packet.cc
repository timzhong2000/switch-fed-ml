#include "packet.h"
#include <cstdlib>

namespace switchml
{
  int sizeofDataType(DataType data_type)
  {
    return 4;
  }

  Packet::Packet()
  {
    this->buffer = malloc(DATA_LEN + sizeof(SwitchmlHeader));
    this->header = reinterpret_cast<SwitchmlHeader *>(this->buffer);
    this->data = reinterpret_cast<void *>(this->header + 1);
  }

  Packet::Packet(Packet &&pkt)
  {
    this->buffer = pkt.buffer;
    this->header = pkt.header;
    this->data = pkt.data;
    pkt.buffer = nullptr;
    pkt.header = nullptr;
    pkt.data = nullptr;
  }

  Packet::~Packet()
  {
    if (this->buffer)
    {
      free(this->buffer);
    }
  }
}