#ifndef _SWITCH_FL_PARSER
#define _SWITCH_FL_PARSER

#include "type.p4"

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
            0x0806:  parse_arp;
            default: accept;
        }
    }

    state parse_arp {
        pkt.extract(hdr.arp);
        transition accept;
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

#endif