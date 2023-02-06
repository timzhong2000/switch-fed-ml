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
  action set_group_config(AggregateNum_t total_aggregate_num, bit<32> aggregate_finish_bitmap){
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

    size = 128;
    default_action = drop;
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
      drop;
      set_bitmap;
    }

    size = 128;
    default_action = drop;
  }
  // bitmap end

  apply {
    group_config.apply();
    worker_bitmap.apply();
  }
}

#endif
