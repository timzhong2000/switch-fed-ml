#ifndef _SWITCH_FL_MAIN
#define _SWITCH_FL_MAIN

#define DEBUG
#define POOL_SIZE 128

#include <core.p4>
#include <v1model.p4>
#include "type.p4"
#include "receiver.p4"
#include "processor.p4"
#include "sender.p4"

parser MyIngressParser(
    packet_in pkt,
    out headers_t hdr,
    inout metadata_t meta,
    inout standard_metadata_t standard_meta)
{
    state start {
        pkt.extract(hdr.ethernet);
        transition select(hdr.ethernet.ether_type) {
            0x0800:  parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        pkt.extract(hdr.ipv4);
        // verify(hdr.ipv4.version == 4w4, error.IPv4IncorrectVersion);
        // verify(hdr.ipv4.ihl == 4w5, error.IPv4OptionsNotSupported);
        transition select(hdr.ipv4.ihl, hdr.ipv4.frag_offset, hdr.ipv4.protocol) {
            (5, 0, 17): parse_udp;
            default: accept;
        }
    }

    state parse_udp {
        pkt.extract(hdr.udp);
        transition select(hdr.udp.dst_port) {
            SwitchFL_PORT: parse_switchfl;
            default: accept;
        }
    }

    state parse_switchfl {
        pkt.extract(hdr.switchfl);
        pkt.extract(hdr.tensor0);
        pkt.extract(hdr.tensor1);
        pkt.extract(hdr.tensor2);
        pkt.extract(hdr.tensor3);
        pkt.extract(hdr.tensor4);
        pkt.extract(hdr.tensor5);
        pkt.extract(hdr.tensor6);
        pkt.extract(hdr.tensor7);
        transition accept;
    }
}

control MyVerifyChecksum(
    inout headers_t hdr,
    inout metadata_t meta)
{
    apply { }
}

control MyIngress(
    inout headers_t hdr,
    inout metadata_t meta,
    inout standard_metadata_t standard_meta)
{
    Receiver() switchfl_receiver;
    Processor() processor;

    action drop_action() {
        mark_to_drop(standard_meta);
    }

    action to_port_action(bit<9> port) {
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
        standard_meta.egress_spec = port;
    }

    action switchfl_send_back_action() {
        standard_meta.egress_spec = standard_meta.ingress_port;
        standard_meta.egress_port = standard_meta.ingress_port;
    }

    action switchfl_multicast_action() {
        standard_meta.mcast_grp = hdr.switchfl.mcast_grp;
        standard_meta.egress_spec = 0;
        standard_meta.egress_port = 0;
    }

    // 不可能进入的分支
    action switchfl_error_catch_action() {}

    table ipv4_match {
        key = {
            hdr.ipv4.dst_addr: lpm;
        }
        actions = {
            drop_action;
            to_port_action;
        }
        #ifndef DEBUG
        size = 128;
        #else
        const entries = {
            (0x0b0b0b01) : to_port_action(0); // 11.11.11.1 => port 0
            (0x0b0b0b02) : to_port_action(1); // 11.11.11.2 => port 1
            (0x0b0b0b03) : to_port_action(2); // 11.11.11.3 => port 2
        }
        #endif
        default_action = drop_action;
    }

    apply {
        if(hdr.switchfl.isValid() && hdr.switchfl.bypass == 0) {
            if (hdr.switchfl.multicast == 0) {
                // multicast == 0 说明包不是来自 ps 的
                switchfl_receiver.apply(hdr, meta, standard_meta);
                processor.apply(hdr, meta);
            } else {
                meta.processor_action = Processor_Action.MCAST;
            }
            if(meta.processor_action == Processor_Action.DROP) {
                drop_action();
            } else if (meta.processor_action == Processor_Action.ECN || meta.processor_action == Processor_Action.ACK) {
                switchfl_send_back_action();
            } else if (meta.processor_action == Processor_Action.MCAST || meta.processor_action == Processor_Action.FINISH) {
                switchfl_multicast_action();
            } else {
                switchfl_error_catch_action();
            }
        } else {
            ipv4_match.apply();
        }
    }
}

control MyEgress(
    inout headers_t hdr,
    inout metadata_t meta,
    inout standard_metadata_t standard_meta)
{
    Sender() switchfl_sender;

    action set_tensor_invalid() {
        hdr.tensor0.setInvalid();
        hdr.tensor1.setInvalid();
        hdr.tensor2.setInvalid();
        hdr.tensor3.setInvalid();
        hdr.tensor4.setInvalid();
        hdr.tensor5.setInvalid();
        hdr.tensor6.setInvalid();
        hdr.tensor7.setInvalid();
        hdr.ipv4.total_len = hdr.ipv4.total_len - 1024;
        hdr.udp.length = hdr.udp.length - 1024;
    }

    action switchfl_mark_to_emit_payload() {
        // do nothing
    }

    action switchfl_mark_to_ack() {
        hdr.switchfl.ack = 1;
        set_tensor_invalid();
    }

    action switchfl_mark_to_ecn() {
        hdr.switchfl.ecn = 1;
        set_tensor_invalid();
    }

    action switchfl_mark_to_drop() {
        mark_to_drop(standard_meta);
        set_tensor_invalid();
    }

    apply {
        if(hdr.switchfl.isValid() && hdr.switchfl.bypass == 0) {
            switchfl_sender.apply(hdr, meta, standard_meta);
            // 约定 egress_rid == 9999 为向 ps 发送的标记
            if(meta.processor_action == Processor_Action.FINISH) {
                if(meta.is_ps) {
                    switchfl_mark_to_emit_payload();
                } else {
                    switchfl_mark_to_ack();
                }
            } else if(meta.processor_action == Processor_Action.MCAST) {
                if(meta.is_ps) {
                    switchfl_mark_to_drop();
                } else {
                    switchfl_mark_to_emit_payload();
                }
            } else if(meta.processor_action == Processor_Action.ECN) {
                switchfl_mark_to_ecn();
            } else if(meta.processor_action == Processor_Action.ACK) {
                switchfl_mark_to_ack();
            } else if(meta.processor_action == Processor_Action.DROP) {
                switchfl_mark_to_drop();
            }
        }
    }
}

control MyComputeChecksum(
    inout headers_t hdr,
    inout metadata_t meta)
{
    apply {
        update_checksum(
            hdr.ipv4.isValid(),
            {
                hdr.ipv4.version,
                hdr.ipv4.ihl,
                hdr.ipv4.diffserv,
                hdr.ipv4.total_len,
                hdr.ipv4.identification,
                hdr.ipv4.flags,
                hdr.ipv4.frag_offset,
                hdr.ipv4.ttl,
                hdr.ipv4.protocol,
                hdr.ipv4.src_addr,
                hdr.ipv4.dst_addr
            },
            hdr.ipv4.hdr_checksum,
            HashAlgorithm.csum16
        );
        update_checksum(
            hdr.udp.isValid(),
            {
                hdr.udp.src_port,
                hdr.udp.dst_port,
                hdr.udp.length
            },
            hdr.udp.checksum,
            HashAlgorithm.csum16
        );
    }
}

control MyEgressDeparser(
    packet_out pkt,
    in headers_t hdr)
{
    apply {
        pkt.emit(hdr);
    }
}

V1Switch(
    MyIngressParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyEgressDeparser()
) main;

#endif