#ifndef SWITCH_FED_ML_CLIENT_H
#define SWITCH_FED_ML_CLIENT_H

#include "node.h"

namespace switchml
{
  class Client : public Node
  {
  public:
    Client(NodeOptions options);
  };
}
#endif