#ifndef _SWITCH_FL_MAIN
#define _SWITCH_FL_MAIN

// #define DEBUG
#define POOL_SIZE 1024

#include <core.p4>
#include <v1model.p4>
#include "type.p4"
#include "receiver.p4"
#include "processor.p4"
#include "sender.p4"
#include "checksum.p4"
#include "parser.p4"
#include "ingress.p4"
#include "egress.p4"
// #include "arp_table.p4"

control MyVerifyChecksum(
    inout headers_t hdr,
    inout metadata_t meta)
{
    apply { }
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