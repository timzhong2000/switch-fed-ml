#ifndef SWITCH_FED_ML_SERVER_H
#define SWITCH_FED_ML_SERVER_H

#include <vector>
#include <memory>
#include "node.h"
#include "tensor.h"

namespace switchml
{
  class Server : public Node
  {
  public:
    Server(std::string ip_addr, uint16_t port);

    ~Server();

    /** multicast to node_list */
    int multicast(std::vector<std::shared_ptr<Node>> &node_list, Tensor &tensor);

    /** reduce from node_list */
    int reduce(std::vector<std::shared_ptr<Node>> &node_list, Tensor &tensor);

  private:
    /** 广播和聚合过程，可以直接对最近的 switch 进行操作而不是对节点操作 */
    std::vector<std::shared_ptr<Node>> optimize(std::vector<std::shared_ptr<Node>> &node_list);
  };
}
#endif