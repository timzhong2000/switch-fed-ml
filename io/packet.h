#ifndef SWITCH_FED_ML_PACKET_H
#define SWITCH_FED_ML_PACKET_H

#include <cstdint>
#include "type.h"

namespace switchml
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
    
    int size();

  private:
  };

  int sizeofDataType(DataType data_type);
}

#endif