#ifndef _SWITCH_FL_RECEIVER
#define _SWITCH_FL_RECEIVER

#include "type.p4"

control Receiver(
  in headers_t hdr,
  inout metadata_t meta,
  inout standard_metadata_t standard_meta
) {
  
  action drop() {
    mark_to_drop(standard_meta);
  }

  // group config start
  action set_group_config(AggregateNum_t total_aggregate_num, bit<32> aggregate_finish_bitmap) {
    meta.total_aggregate_num = total_aggregate_num;
    meta.aggregate_finish_bitmap = aggregate_finish_bitmap;
  }

  table group_config {
    key = {
      hdr.switchfl.mcast_grp: exact;
    }
    actions = {
      set_group_config;
      drop;
    }

    #ifndef DEBUG
    size = 128;
    #else
    const entries = {
      (1): set_group_config(1, 0x0001); // node_id = 1
      (2): set_group_config(2, 0x0003); // node_id = 1 & 2
      (3): set_group_config(3, 0x0007); // node_id = 1 & 2 & 3
    }
    #endif
    const default_action = drop;
  }
  // group config end

  // bitmap start
  action set_bitmap(WorkerBitmap_t bitmap) {
    meta.bitmap = bitmap;
  }

  // map worker to bitmap
  table worker_bitmap {
    key = {
      hdr.switchfl.node_id: exact;
    }
    actions = {
      set_bitmap;
      drop;
    }

    #ifndef DEBUG
    size = 128;
    #else
    const entries = {
      (1): set_bitmap(0x0001);
      (2): set_bitmap(0x0002);
      (3): set_bitmap(0x0004);
    }
    #endif
    
    const default_action = drop;
  }
  // bitmap end

  apply {
    group_config.apply();
    worker_bitmap.apply();
  }
}

#endif
