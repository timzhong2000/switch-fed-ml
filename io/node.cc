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

  int Node::send(Node &node, std::shared_ptr<Tensor> tensor)
  {
    // 拆包
    // 每个 packet 容纳的 element 数量
    uint32_t elements_per_packet = (DATA_LEN / sizeofDataType(tensor->data_type));
    uint32_t total_packet_num = tensor->len / elements_per_packet;
    uint32_t receive_cnt = 0;

    // TODO: rpc 通知对方节点进行接收

    // 发送
    // TODO: 支持 sendBurst，暂时为了 debug 一个个发
    Packet pkt;
    for (size_t i = 0; i < total_packet_num; i++)
    {
      uint32_t offset = i * elements_per_packet; // offset of elements
      pkt.header->aggregate_num = 1;
      pkt.header->bypass = false;
      pkt.header->data_type = tensor->data_type;
      pkt.header->ecn = false;
      pkt.header->offset = offset;
      pkt.header->tensor_id = tensor->tensor_id;
      pkt.header->ucast_grp = 0;
      memcpy(pkt.data, tensor->seek(offset), elements_per_packet * sizeofDataType(tensor->data_type)); // TODO: 优化指针传递而不是拷贝
      this->send_to_udp(node, pkt);
    }

    return 0;
  }

  int Node::send_to_udp(Node &node, Packet &pkt)
  {
    auto dst_endpoint = ip::udp::endpoint(ip::address::from_string(node.options.ip_addr), node.options.port);
    auto sent = this->socket.send_to(buffer(pkt.buffer, pkt.size()), dst_endpoint, 0);
    return 0;
  }

  int Node::receive_from_udp(Packet &pkt)
  {
    this->socket.receive(buffer(pkt.buffer, pkt.size()));
    return 0;
  }

  int Node::receive(Node &node, std::shared_ptr<Tensor> tensor)
  {
    uint32_t elements_per_packet = (DATA_LEN / sizeofDataType(tensor->data_type));
    uint32_t total_packet_num = tensor->len / elements_per_packet;
    uint32_t receive_cnt = 0;

    Bitmap bitmap(total_packet_num);
    Packet pkt;

    while (receive_cnt < total_packet_num)
    {
      this->receive_from_udp(pkt);
      tensor->write(pkt.data, pkt.header->offset, elements_per_packet);
      bitmap.set(pkt.header->offset / elements_per_packet, true);
      receive_cnt++;
    }
    return 0;
  }

  int Node::addChild(std::shared_ptr<Node> node)
  {
    this->children.push_back(node);
    return 0;
  }

  int Node::removeChild(std::shared_ptr<Node> node)
  {
    for (size_t i = 0; i < this->children.size(); i++)
    {
      if (children[i] == node)
      {
        this->children.erase(this->children.begin() + i);
      }
    }
    return 0;
  }
}