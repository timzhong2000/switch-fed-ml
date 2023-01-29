#include "node.h"
#include <boost/asio.hpp>

#define SEND_WINDOW_SIZE 1 // 每次同时向外发送 SEND_WINDOW_SIZE 个包

namespace switchml
{
  Node::Node(NodeOptions options) : options(options), io_service(), socket(io_service, ip::udp::endpoint(ip::udp::v4(), options.port)){};

  Node::~Node()
  {
    this->socket.close();
  }

  int Node::send(Node &node, GroupId group_id, std::shared_ptr<Tensor> tensor)
  {
    this->pending_tx_tensors.insert({tensor->tensor_id, tensor});
    // 拆包
    // 每个 packet 容纳的 element 数量
    uint32_t elements_per_packet = (DATA_LEN / sizeofDataType(tensor->data_type));
    uint32_t total_packet_num = tensor->len / elements_per_packet;
    uint32_t receive_cnt = 0;

    // TODO: rpc 通知对方节点进行接收

    // 全部
    // TODO: 支持 sendBurst，支持 ecn
    Packet pkt;
    for (size_t i = 0; i < total_packet_num; i++)
    {
      Offset offset = i * elements_per_packet; // offset of elements
      pkt.header->aggregate_num = 1;
      pkt.header->bypass = false;
      pkt.header->data_type = tensor->data_type;
      pkt.header->node_id = this->options.node_id;
      pkt.header->ecn = false;
      pkt.header->offset = offset;
      pkt.header->tensor_id = tensor->tensor_id;
      pkt.header->ucast_grp = group_id;
      memcpy(pkt.data, tensor->seek(offset), elements_per_packet * sizeofDataType(tensor->data_type)); // TODO: 优化指针传递而不是拷贝
      this->send_to_udp(node, pkt);
    }

    // TODO: 等待对方节点确认接收完毕再清理资源

    // 清理资源
    this->pending_tx_tensors.erase(tensor->tensor_id);
    return 0;
  }

  size_t Node::send_to_udp(Node &node, Packet &pkt)
  {
    auto dst_endpoint = ip::udp::endpoint(ip::address::from_string(node.options.ip_addr), node.options.port);
    auto sent = this->socket.send_to(buffer(pkt.buffer, pkt.size()), dst_endpoint, 0);
    return 0;
  }

  int Node::receive(Node &node, GroupId group_id, std::shared_ptr<Tensor> tensor)
  {
    // 拆包
    // 每个 packet 容纳的 element 数量
    uint32_t elements_per_packet = (DATA_LEN / sizeofDataType(tensor->data_type));
    uint32_t total_packet_num = tensor->len / elements_per_packet;
    uint32_t receive_cnt = 0;

    auto key = std::make_tuple(tensor->tensor_id, node.options.node_id);
    auto bitmap = std::make_shared<Bitmap>(total_packet_num);
    this->pending_rx_bitmaps.insert({key, bitmap});
    this->pending_rx_tensors.insert({key, tensor});
    // TODO: wait until tensor loaded

    // 假设超时为 1 秒，检查 bitmap 处理丢包重传
    sleep(1);

    this->pending_rx_tensors.erase(key);
    this->pending_rx_bitmaps.erase(key);

    return 0;
  }

  // server 和 worker 节点启动的时候，启动接收线程，这里需要保证单线程写入 tensor
  void Node::receive_loop()
  {
    Packet pkt;
    while (1)
    {
      this->socket.receive(buffer(pkt.buffer, pkt.size()));
      auto key = std::make_tuple(pkt.header->tensor_id, pkt.header->node_id);
      auto tensor = this->pending_rx_tensors.find(key)->second;
      auto bitmap = this->pending_rx_bitmaps.find(key)->second;
      if (!tensor)
      {
        // 说明这个包到来的时机太晚，已经进入了重传流程，直接丢弃
        continue;
      }
      uint32_t elements_per_packet = (DATA_LEN / sizeofDataType(tensor->data_type));
      tensor->write(pkt.data, pkt.header->offset, elements_per_packet);
      bitmap->set(pkt.header->offset / elements_per_packet, true);
    }
  }

  int Node::addChild(std::shared_ptr<Node> node)
  {
    this->children.insert({node->options.node_id, node});
    return 0;
  }

  int Node::removeChild(std::shared_ptr<Node> node)
  {
    this->children.erase(node->options.node_id);
    return 0;
  }

  size_t Node::rpc_retransmission(Node &node, GroupId group_id, std::vector<Offset> &missing_packet_offset_list, Offset slice_len, Tensor &tensor)
  {
    // TODO: 可靠传输
    // 如果是 switch，需要模拟聚合
    return 0;
  }
}