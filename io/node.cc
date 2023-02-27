#include "node.h"
#include <boost/asio.hpp>

#define SEND_WINDOW_SIZE 64 // 每次同时向外发送 SEND_WINDOW_SIZE 个包

namespace switchfl
{
  Node::Node(NodeOptions options) : options(options), io_service(), socket(io_service, ip::udp::endpoint(ip::udp::v4(), options.port)){};

  Node::~Node()
  {
    this->socket.close();
  }

  int Node::send(Node &node, GroupId group_id, std::shared_ptr<Tensor> tensor)
  {
    // std::vector<std::thread> threads;
    // threads.push_back(std::thread([&]
    //                               { this->send_thread(node, 0, group_id, tensor); }));

    // for (size_t i = 0; i < this->tx_window_size; i++)
    // {
    //   threads[i].join();
    // }

    auto send_socket = ip::udp::socket(this->io_service, ip::udp::endpoint(ip::udp::v4(), 60000));

    // 拆包
    // 每个 packet 容纳的 element 数量
    uint32_t elements_per_packet = (DATA_LEN / sizeofDataType(tensor->data_type));
    // 当前线程应该发送的包数量
    uint32_t total_packet_num = tensor->len / elements_per_packet;

    auto dst_endpoint = ip::udp::endpoint(ip::address::from_string(node.options.ip_addr), node.options.port);

    Packet tx_pkt;
    Packet rx_pkt;

    for (size_t i = 0; i < total_packet_num; i++)
    {
      tx_pkt.header->flow_control = 0;
      tx_pkt.header->aggregate_num = 1;
      tx_pkt.header->data_type = tensor->data_type;
      tx_pkt.header->node_id = this->options.node_id;
      tx_pkt.header->packet_id = i;
      tx_pkt.header->round_id = tensor->round_id;
      tx_pkt.header->ucast_grp = group_id;
      memcpy(tx_pkt.data, tensor->seek(tx_pkt.header->packet_id * elements_per_packet), elements_per_packet * sizeofDataType(tensor->data_type));
      while (true)
      {
        auto sent = send_socket.send_to(buffer(tx_pkt.buffer, tx_pkt.size()), dst_endpoint, 0);
        // auto recv = send_socket.receive(buffer(rx_pkt.buffer, rx_pkt.size()));
        // if (rx_pkt.isAck())
          break;
      }
    }

    return 0;
  }

  void Node::send_thread(Node &node, int send_window_index, GroupId group_id, std::shared_ptr<Tensor> tensor)
  {
  }

  int Node::receive(Node &node, GroupId group_id, std::shared_ptr<Tensor> tensor)
  {
    uint32_t elements_per_packet = (DATA_LEN / sizeofDataType(tensor->data_type));
    uint32_t total_packet_num = tensor->len / elements_per_packet;

    auto key = std::make_tuple(tensor->round_id, node.options.node_id);
    auto bitmap = std::make_shared<Bitmap>(total_packet_num);
    auto job = std::make_shared<Job>(tensor, bitmap);
    this->rx_jobs.insert(std::make_pair(key, job));

    sleep(2);
    // job->wait_until_job_finish();
    // job->finish();

    this->rx_jobs.erase(key);
    int cnt = 0;
    for (size_t i = 0; i < total_packet_num; i++)
    {
      cnt += job->bitmap->get(i);
    }

    return 0;
  }

  // server 和 worker 节点启动的时候，启动接收线程，这里需要保证单线程写入 tensor
  void Node::receive_thread()
  {
    Packet pkt;
    ip::udp::endpoint ep;
    while (1)
    {
      this->socket.receive_from(buffer(pkt.buffer, pkt.size()), ep);
      auto key = std::make_tuple(pkt.header->round_id, pkt.header->node_id);
      auto job = this->rx_jobs.find(key)->second;
      if (!job)
      {
        // 没有接收任务，直接忽略
        continue;
      }
      job->handle_packet(pkt);
      pkt.setAck(true);
      this->socket.send_to(buffer(pkt.buffer, sizeof(SwitchmlHeader)), ep);
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

  size_t Node::rpc_retransmission(Node &node, GroupId group_id, std::vector<PacketId> &missing_packet_id_list, PacketId slice_len, std::shared_ptr<Tensor> tensor)
  {
    // TODO: 可靠传输
    // 如果是 switch，需要模拟聚合
    return 0;
  }
}