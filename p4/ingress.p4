#ifndef _SWITCH_FL_INGRESS
#define _SWITCH_FL_INGRESS

#include "receiver.p4"
#include "processor.p4"
#include "type.p4"

control MyIngress(
    inout headers_t hdr,
    inout metadata_t meta,
    inout standard_metadata_t standard_meta)
{
    Receiver() switchfl_receiver;
    Processor() processor;
    // ArpTable() arp_table;

    action drop_action() {
        mark_to_drop(standard_meta);
    }

    action to_port_action(bit<9> port) {
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
        standard_meta.egress_spec = port;
    }

    action switchfl_send_back_action() {
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
        } else if (hdr.ipv4.isValid()){
            ipv4_match.apply();
        } else if (hdr.arp.isValid()) {
            // arp_table.apply(hdr, meta, standard_meta);
        }
    }
}
#endif
