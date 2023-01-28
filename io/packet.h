#ifndef SWITCH_FED_ML_PACKET_H
#define SWITCH_FED_ML_PACKET_H

#include <cstdint>
#include "type.h"

namespace switchml
{

  class Packet
  {
  public:
    SwitchmlHeader *header;
    void *data;

    Packet();

    Packet(Packet &pkt) = delete;

    Packet(Packet &&pkt);

  private:
    void *buffer;
  };

  int sizeofDataType(DataType data_type);
}

#endif