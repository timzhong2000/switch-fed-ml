#include "server.h"

namespace switchml
{
  int Server::multicast(std::vector<std::shared_ptr<Node>> &node_list, std::shared_ptr<Tensor> &tensor)
  {
    auto node_list_to_send = this->optimize(node_list);
    std::vector<std::thread> threads;

    for (auto node : node_list_to_send)
    {
      threads.push_back(std::thread([this, node, tensor]
                                    { this->send(*node, tensor); }));
    }

    while (!threads.empty())
    {
      threads.back().join();
      threads.pop_back();
    }

    return 0;
  }

  int Server::reduce(std::vector<std::shared_ptr<Node>> &node_list, std::shared_ptr<Tensor> &tensor)
  {
    auto node_list_to_receive = this->optimize(node_list);
    std::vector<std::shared_ptr<Tensor>> tensor_buffer;
    tensor_buffer.reserve(node_list_to_receive.size());
    std::vector<std::thread> threads;

    for (auto node : node_list_to_receive)
    {
      auto temp_tensor = std::make_shared<Tensor>(tensor->len, tensor->data_type, tensor->tensor_id);
      tensor_buffer.push_back(temp_tensor);
      threads.push_back(std::thread([this, node, temp_tensor]
                                    { this->receive(*node, temp_tensor); }));
    }

    while (!threads.empty())
    {
      threads.back().join();
      threads.pop_back();
    }

    // 重新聚合
    int aggregate_num = 0;
    for (auto temp_tensor : tensor_buffer)
    {
      aggregate_num += tensor->aggregate_num;
      tensor->add(*temp_tensor);
    }
    tensor->divide(aggregate_num);

    return 0;
  }

  std::vector<std::shared_ptr<Node>> Server::optimize(std::vector<std::shared_ptr<Node>> &node_list)
  {
    // TODO: 根据 node_tree 分析最优发送方案
    return node_list;
  }

}