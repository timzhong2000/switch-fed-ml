#pragma once

#include <cstdint>
#include "type.h"

namespace switchfl
{

  class Packet
  {
  public:
    void *buffer;
    SwitchmlHeader *header;
    void *data;

    Packet();

    Packet(Packet &pkt) = delete;

    Packet(Packet &&pkt);

    ~Packet();

    void setAck(bool val);
    void setEcn(bool val);
    bool isAck();
    bool isEcn();

    int size();

  private:
  };

  int sizeofDataType(uint8_t data_type);
}