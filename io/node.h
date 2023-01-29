#ifndef SWITCH_FED_ML_NODE_H
#define SWITCH_FED_ML_NODE_H

#include <string>
#include <vector>
#include <memory>
#include <map>
#include "tensor.h"
#include <boost/asio.hpp>
#include "bitmap.h"
#include <tuple>

using namespace boost::asio;

namespace switchml
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

    void receive_loop();

  private:
    std::map<NodeId, std::shared_ptr<Node>> children;
    std::shared_ptr<Node> parent;

    std::map<TensorId, std::shared_ptr<Tensor>> pending_tx_tensors;
    std::map<std::tuple<TensorId, NodeId>, std::shared_ptr<Tensor>> pending_rx_tensors;
    std::map<std::tuple<TensorId, NodeId>, std::shared_ptr<Bitmap>> pending_rx_bitmaps;

    boost::asio::io_service io_service;
    ip::udp::socket socket;

    // TODO: rpc endpoint，client 和 server 都提供 rpc 端点，用于同步以及可靠重传

    size_t send_to_udp(Node &node, Packet &pkt);

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
    size_t rpc_retransmission(Node &node, GroupId group_id, std::vector<Offset> &missing_packet_offset_list, Offset slice_len, Tensor &tensor);
  };
}
#endif