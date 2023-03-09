#ifndef _SWITCH_FL_PROCESSOR
#define _SWITCH_FL_PROCESSOR

#include "type.p4"
#include "tensor_buffer.p4"


control Processor (
  inout headers_t hdr,
  inout metadata_t meta
)
{
  TensorBuffer() tensor_buffer_0;
  TensorBuffer() tensor_buffer_1;
  TensorBuffer() tensor_buffer_2;
  TensorBuffer() tensor_buffer_3;
  TensorBuffer() tensor_buffer_4;
  TensorBuffer() tensor_buffer_5;
  TensorBuffer() tensor_buffer_6;
  TensorBuffer() tensor_buffer_7;

  register<bit<32>>(POOL_SIZE) aggregate_bitmap;
  register<RoundId_t>(POOL_SIZE) current_round_id;
  register<SegmentId_t>(POOL_SIZE) current_segment_id;
  register<bit<16>>(POOL_SIZE) aggregate_count;
  register<bit<1>>(POOL_SIZE) is_busy;

  action release(bit<32> pool_id) {
    is_busy.write(pool_id, 0);
    aggregate_bitmap.write(pool_id, 0);
  }

  action acquire(bit<32> pool_id) {
    current_round_id.write(pool_id, hdr.switchfl.round_id);
    current_segment_id.write(pool_id, hdr.switchfl.segment_id);
    is_busy.write(pool_id, 1);
    aggregate_bitmap.write(pool_id, 0);
  }

  action mark_action_to_ack(){
    meta.processor_action = Processor_Action.ACK;
  }

  action mark_action_to_mcast(){
    meta.processor_action = Processor_Action.MCAST;
  }

  action mark_action_to_finish(){
    meta.processor_action = Processor_Action.FINISH;
  }

  action mark_action_to_drop(){
    meta.processor_action = Processor_Action.DROP;
  }

  action mark_action_to_ecn(){
    meta.processor_action = Processor_Action.ECN;
  }

  action add_aggregate_count(bit<32> pool_id) {
    bit<16> current_pool_aggregate_count;
    aggregate_count.read(current_pool_aggregate_count, pool_id);
    current_pool_aggregate_count = current_pool_aggregate_count + hdr.switchfl.aggregate_num;
    aggregate_count.write(pool_id, current_pool_aggregate_count);
  }

  apply {
    bit<32> pool_id = (bit<32>)hdr.switchfl.pool_id;

    bit<1> current_pool_is_busy;
    SegmentId_t current_pool_segment_id;
    RoundId_t current_pool_round_id;
    is_busy.read(current_pool_is_busy, pool_id);
    current_segment_id.read(current_pool_segment_id, pool_id);
    current_round_id.read(current_pool_round_id, pool_id);

    if ((hdr.switchfl.round_id > current_pool_round_id) || (hdr.switchfl.round_id == current_pool_round_id && hdr.switchfl.segment_id > current_pool_segment_id)) {
      // 为新包申请聚合器
      acquire(pool_id);
      aggregate_bitmap.write(pool_id, meta.bitmap);
      if (current_pool_is_busy == 1) {
        // 发出部分聚合的包
        ////////////////////do swap//////////////////////
        tensor_buffer_0.apply(hdr.tensor0, pool_id, 0);
        tensor_buffer_1.apply(hdr.tensor1, pool_id, 0);
        tensor_buffer_2.apply(hdr.tensor2, pool_id, 0);
        tensor_buffer_3.apply(hdr.tensor3, pool_id, 0);
        tensor_buffer_4.apply(hdr.tensor4, pool_id, 0);
        tensor_buffer_5.apply(hdr.tensor5, pool_id, 0);
        tensor_buffer_6.apply(hdr.tensor6, pool_id, 0);
        tensor_buffer_7.apply(hdr.tensor7, pool_id, 0);
        hdr.switchfl.round_id = current_pool_round_id;
        hdr.switchfl.segment_id = current_pool_segment_id;
        bit<16> current_pool_aggregate_count;
        aggregate_count.read(current_pool_aggregate_count, pool_id);
        hdr.aggregate_count = current_pool_aggregate_count;
        /////////////////////////////////////////////////
        mark_action_to_finish();
      } else {
        ////////////////////do write//////////////////////
        tensor_buffer_0.apply(hdr.tensor0, pool_id, 2);
        tensor_buffer_1.apply(hdr.tensor1, pool_id, 2);
        tensor_buffer_2.apply(hdr.tensor2, pool_id, 2);
        tensor_buffer_3.apply(hdr.tensor3, pool_id, 2);
        tensor_buffer_4.apply(hdr.tensor4, pool_id, 2);
        tensor_buffer_5.apply(hdr.tensor5, pool_id, 2);
        tensor_buffer_6.apply(hdr.tensor6, pool_id, 2);
        tensor_buffer_7.apply(hdr.tensor7, pool_id, 2);
        /////////////////////////////////////////////////
        if (meta.aggregate_finish_bitmap == meta.bitmap) {
          // 单节点
          mark_action_to_finish();
          release(pool_id);
        } else {
          aggregate_bitmap.write(pool_id, meta.bitmap);
          mark_action_to_drop();
        }
      }
    } else if (hdr.switchfl.round_id == current_pool_round_id && hdr.switchfl.segment_id == current_pool_segment_id && current_pool_is_busy == 1) {
      // 正常聚合，且当前聚合器有正在执行的任务
      bit<32> current_pool_bitmap;
      aggregate_bitmap.read(current_pool_bitmap, pool_id);
      // 检查当前 worker_bitmap 在当前聚合器是否聚合过，如果聚合过说明是重传包，直接 ack
      if((current_pool_bitmap & meta.bitmap) > 0) {
        mark_action_to_ack();
        return;
      }
      current_pool_bitmap = current_pool_bitmap | meta.bitmap;
      aggregate_bitmap.write(pool_id, current_pool_bitmap);

      ////////////////////do_aggregate//////////////////
      add_aggregate_count(pool_id);
      tensor_buffer_0.apply(hdr.tensor0, pool_id, 1);
      tensor_buffer_1.apply(hdr.tensor1, pool_id, 1);
      tensor_buffer_2.apply(hdr.tensor2, pool_id, 1);
      tensor_buffer_3.apply(hdr.tensor3, pool_id, 1);
      tensor_buffer_4.apply(hdr.tensor4, pool_id, 1);
      tensor_buffer_5.apply(hdr.tensor5, pool_id, 1);
      tensor_buffer_6.apply(hdr.tensor6, pool_id, 1);
      tensor_buffer_7.apply(hdr.tensor7, pool_id, 1);
      //////////////////////////////////////////////////
      
      if(current_pool_bitmap == meta.aggregate_finish_bitmap) {
        // 聚合完成
        mark_action_to_finish();
        release(pool_id);
      } else {
        mark_action_to_drop();
      }
    } else {
      // 包落后聚合器
      mark_action_to_ack();
      return;
    }
  }
}


#endif