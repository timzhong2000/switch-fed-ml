#pragma once

#include "node.h"

namespace switchfl
{
  class Client : public Node
  {
  public:
    Client(NodeOptions options);
  };
}