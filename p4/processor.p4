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
  register<TensorId_t>(POOL_SIZE) current_tensor_id;
  register<SegmentId_t>(POOL_SIZE) current_segment_id;
  register<bit<1>>(POOL_SIZE) is_busy;


  action release(bit<32> pool_id) {
    is_busy.write(pool_id, 0);
    aggregate_bitmap.write(pool_id, 0);
  }

  action acquire(bit<32> pool_id) {
    current_tensor_id.write(pool_id, hdr.switchfl.tensor_id);
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

  apply {
    bit<1> current_pool_is_busy;
    bit<32> pool_id = (bit<32>)hdr.switchfl.pool_id;

    // 多任务时可能会出现竞争
    is_busy.read(current_pool_is_busy, pool_id);
    if(current_pool_is_busy == 0) {
      if(hdr.switchfl.retranmission == 1) { 
          // 这种情况是 client 没有收到 ack 进行了错误的超时重传。此时已经在聚合下一个包，应该通知 client 结束重传
          mark_action_to_ack();
          return;
      }
      acquire(pool_id);
    } else {
      bit<32> current_pool_segment_id;
      bit<32> current_pool_tensor_id;
      current_segment_id.read(current_pool_segment_id, pool_id);
      current_tensor_id.read(current_pool_tensor_id, pool_id);
      if(hdr.switchfl.segment_id != current_pool_segment_id || hdr.switchfl.tensor_id != current_pool_tensor_id) {
        if(hdr.switchfl.retranmission == 1) { 
          // 这种情况是 client 没有收到 ack 进行了错误的超时重传。此时已经在聚合下一个包，应该通知 client 结束重传
          mark_action_to_ack();
        } else {
          // 这种情况是多任务场景下，两个任务使用同一个聚合器，后到的任务应该等待
          mark_action_to_ecn();
        }
        return;
      }
    }

    bit<32> current_pool_bitmap;
    // 处理重传包，然后检查聚合完成状态
    aggregate_bitmap.read(current_pool_bitmap, pool_id);
    // 检查当前 worker_bitmap 在当前聚合器是否聚合过，如果聚合过说明是重传包，直接 ack
    if(current_pool_bitmap & meta.bitmap > 0) {
      mark_action_to_ack();
      return;
    }
    current_pool_bitmap = current_pool_bitmap | meta.bitmap;
    aggregate_bitmap.write(pool_id, current_pool_bitmap);
    
    tensor_buffer_0.apply(hdr.tensor0, pool_id, false);

    if(current_pool_bitmap == meta.aggregate_finish_bitmap) { // 聚合完成
      mark_action_to_finish();
      release(pool_id);
      tensor_buffer_0.apply(hdr.tensor0, pool_id, true); // reset tensor buffer
      tensor_buffer_1.apply(hdr.tensor1, pool_id, true); // reset tensor buffer
      tensor_buffer_2.apply(hdr.tensor2, pool_id, true); // reset tensor buffer
      tensor_buffer_3.apply(hdr.tensor3, pool_id, true); // reset tensor buffer
      tensor_buffer_4.apply(hdr.tensor4, pool_id, true); // reset tensor buffer
      tensor_buffer_5.apply(hdr.tensor5, pool_id, true); // reset tensor buffer
      tensor_buffer_6.apply(hdr.tensor6, pool_id, true); // reset tensor buffer
      tensor_buffer_7.apply(hdr.tensor7, pool_id, true); // reset tensor buffer
    } else {
      mark_action_to_drop();
    }
  }
}


#endif