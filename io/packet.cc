#include "packet.h"
#include <cstdlib>

namespace switchfl
{

  uint8_t ack_bitmap = 1 << 0;
  uint8_t ecn_bitmap = 1 << 1;
  uint8_t bypass_bitmap = 1 << 2;

  int sizeofDataType(uint8_t data_type)
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

  int Packet::size()
  {
    return DATA_LEN + sizeof(SwitchmlHeader);
  }

  void Packet::setAck(bool val)
  {
    this->header->flow_control |= val ? ack_bitmap : !ack_bitmap;
  }

  void Packet::setEcn(bool val)
  {
    this->header->flow_control |= val ? ecn_bitmap : !ecn_bitmap;
  }

  bool Packet::isAck()
  {
    return this->header->flow_control & ack_bitmap;
  }
  
  bool Packet::isEcn()
  {
    return this->header->flow_control & ecn_bitmap;
  }
}