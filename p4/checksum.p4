#ifndef _SWITCH_FL_CHECKSUM
#define _SWITCH_FL_CHECKSUM
#include "type.p4"

control MyVerifyChecksum(
    inout headers_t hdr,
    inout metadata_t meta)
{
    apply { }
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
        // update_checksum(
        //     hdr.switchfl.isValid(),
        //     {
        //         // 伪头部
        //         hdr.ipv4.src_addr,
        //         hdr.ipv4.dst_addr,
        //         8w0,
        //         hdr.ipv4.protocol,
        //         hdr.udp.length,
        //         // udp 头部
        //         hdr.udp.src_port,
        //         hdr.udp.dst_port,
        //         hdr.udp.length,
        //         16w0,
        //         hdr.switchfl.ack,
        //         hdr.switchfl.ecn,
        //         hdr.switchfl.bypass,
        //         hdr.switchfl.multicast,
        //         hdr.switchfl.retranmission,
        //         hdr.switchfl.__reserved,
        //         hdr.switchfl.data_type,
        //         hdr.switchfl.tensor_id,
        //         hdr.switchfl.segment_id,
        //         hdr.switchfl.node_id,
        //         hdr.switchfl.aggregate_num,
        //         hdr.switchfl.mcast_grp,
        //         hdr.switchfl.pool_id
        //     },
        //     hdr.udp.checksum,
        //     HashAlgorithm.csum16);
    }
}
#endif