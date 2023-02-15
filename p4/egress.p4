#ifndef _SWITCH_FL_EGRESS
#define _SWITCH_FL_EGRESS

#include "sender.p4"
#include "type.p4"

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
        if(hdr.udp.isValid()) {
            hdr.udp.checksum = 0;
        }
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
                    switchfl_mark_to_ack();
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

control MyEgressDeparser(
    packet_out pkt,
    in headers_t hdr)
{
    apply {
        pkt.emit(hdr);
    }
}

#endif