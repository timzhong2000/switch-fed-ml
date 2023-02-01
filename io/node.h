#pragma once

#include <string>
#include <vector>
#include <memory>
#include <map>
#include "job.h"
#include "tensor.h"
#include <boost/asio.hpp>
#include "bitmap.h"
#include <tuple>
#include "rw.h"

using namespace boost::asio;

namespace switchfl
{

  enum NodeType
  {
    SERVER,
    SWITCH,
    CLIENT,
  };

  struct NodeOptions
  {
    std::string ip_addr;
    uint16_t port;
    uint16_t rpc_port;
    NodeId node_id;
    bool is_remote; // 是否远程节点
  };

  class Node
  {
  public:
    NodeOptions options;

    Node(NodeOptions options);

    ~Node();

    /**
     * send tensor to node
     * @param node 是抽象的 node，不会使用 node 的有状态部分
     */
    int send(Node &node, GroupId group_id, std::shared_ptr<Tensor> tensor);

    /** receive a tensor from node */
    int receive(Node &node, GroupId group_id, std::shared_ptr<Tensor> tensor);

    /** return -1 when failed */
    int addChild(std::shared_ptr<Node> node);

    /** return -1 when failed */
    int removeChild(std::shared_ptr<Node> node);

    inline NodeType getNodeType()
    {
      if (this->children.size() == 0 && this->parent)
        return NodeType::CLIENT;
      if (!this->parent)
        return NodeType::SERVER;
      return NodeType::SWITCH;
    }

    void receive_thread();

  private:
    // 发送窗口大小，应该小于等于 switch 的 pool size
    int tx_window_size = 1;

    std::map<NodeId, std::shared_ptr<Node>> children;
    std::shared_ptr<Node> parent;

    std::map<std::tuple<TensorId, NodeId>, std::shared_ptr<Job>> rx_jobs;
    
    ReadersWriterLock rx_jobs_lock;

    boost::asio::io_service io_service;
    ip::udp::socket socket;

    // TODO: rpc endpoint，client 和 server 都提供 rpc 端点，用于同步以及可靠重传

    void send_thread(Node &node, int send_window_index, GroupId group_id, std::shared_ptr<Tensor> tensor);

    /**
     * @param offset offset of elemenet, not byte
     */
    void *seek_pending_tensor(TensorId tensor_id, uint32_t offset);

    /**
     * 通过 rpc 从指定 node 读取 tensor 缺失的部分
     * @param node 如果是 switch，则会深度遍历叶子节点完成聚合
     * @param slice_len 每个缺失片段的长度，等于每个 UDP 包 tensor 载荷的数量
     * @return 将会直接写入 tensor
     */
    size_t rpc_retransmission(Node &node, GroupId group_id, std::vector<PacketId> &missing_packet_id_list, PacketId slice_len, std::shared_ptr<Tensor> tensor);
  };
}