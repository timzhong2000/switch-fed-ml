// 每个 tensor buffer 支持长度 128 byte 的 tensor 聚合
control TensorBuffer(
  inout tensor_t tensor,
  in bit<32> pool_id,
  in bool is_reset_action
) {
  register<int<32>>(POOL_SIZE) r0;
  register<int<32>>(POOL_SIZE) r1;
  register<int<32>>(POOL_SIZE) r2;
  register<int<32>>(POOL_SIZE) r3;
  register<int<32>>(POOL_SIZE) r4;
  register<int<32>>(POOL_SIZE) r5;
  register<int<32>>(POOL_SIZE) r6;
  register<int<32>>(POOL_SIZE) r7;
  register<int<32>>(POOL_SIZE) r8;
  register<int<32>>(POOL_SIZE) r9;
  register<int<32>>(POOL_SIZE) r10;
  register<int<32>>(POOL_SIZE) r11;
  register<int<32>>(POOL_SIZE) r12;
  register<int<32>>(POOL_SIZE) r13;
  register<int<32>>(POOL_SIZE) r14;
  register<int<32>>(POOL_SIZE) r15;
  register<int<32>>(POOL_SIZE) r16;
  register<int<32>>(POOL_SIZE) r17;
  register<int<32>>(POOL_SIZE) r18;
  register<int<32>>(POOL_SIZE) r19;
  register<int<32>>(POOL_SIZE) r20;
  register<int<32>>(POOL_SIZE) r21;
  register<int<32>>(POOL_SIZE) r22;
  register<int<32>>(POOL_SIZE) r23;
  register<int<32>>(POOL_SIZE) r24;
  register<int<32>>(POOL_SIZE) r25;
  register<int<32>>(POOL_SIZE) r26;
  register<int<32>>(POOL_SIZE) r27;
  register<int<32>>(POOL_SIZE) r28;
  register<int<32>>(POOL_SIZE) r29;
  register<int<32>>(POOL_SIZE) r30;
  register<int<32>>(POOL_SIZE) r31;

  action aggregate(){
    int<32> temp;
    // loop start
    r0.read(temp, pool_id);
    temp = temp + tensor.d0;
    tensor.d0 = temp;
    r0.write(pool_id, temp);

    r1.read(temp, pool_id);
    temp = temp + tensor.d1;
    tensor.d1 = temp;
    r1.write(pool_id, temp);
    
    r2.read(temp, pool_id);
    temp = temp + tensor.d2;
    tensor.d2 = temp;
    r2.write(pool_id, temp);
    
    r3.read(temp, pool_id);
    temp = temp + tensor.d3;
    tensor.d3 = temp;
    r3.write(pool_id, temp);
    
    r4.read(temp, pool_id);
    temp = temp + tensor.d4;
    tensor.d4 = temp;
    r4.write(pool_id, temp);
    
    r5.read(temp, pool_id);
    temp = temp + tensor.d5;
    tensor.d5 = temp;
    r5.write(pool_id, temp);
    
    r6.read(temp, pool_id);
    temp = temp + tensor.d6;
    tensor.d6 = temp;
    r6.write(pool_id, temp);
    
    r7.read(temp, pool_id);
    temp = temp + tensor.d7;
    tensor.d7 = temp;
    r7.write(pool_id, temp);
    
    r8.read(temp, pool_id);
    temp = temp + tensor.d8;
    tensor.d8 = temp;
    r8.write(pool_id, temp);
    
    r9.read(temp, pool_id);
    temp = temp + tensor.d9;
    tensor.d9 = temp;
    r9.write(pool_id, temp);
    
    r10.read(temp, pool_id);
    temp = temp + tensor.d10;
    tensor.d10 = temp;
    r10.write(pool_id, temp);

    r11.read(temp, pool_id);
    temp = temp + tensor.d11;
    tensor.d11 = temp;
    r11.write(pool_id, temp);

    r12.read(temp, pool_id);
    temp = temp + tensor.d12;
    tensor.d12 = temp;
    r12.write(pool_id, temp);
    
    r13.read(temp, pool_id);
    temp = temp + tensor.d13;
    tensor.d13 = temp;
    r13.write(pool_id, temp);
    
    r14.read(temp, pool_id);
    temp = temp + tensor.d14;
    tensor.d14 = temp;
    r14.write(pool_id, temp);
    
    r15.read(temp, pool_id);
    temp = temp + tensor.d15;
    tensor.d15 = temp;
    r15.write(pool_id, temp);
    
    r16.read(temp, pool_id);
    temp = temp + tensor.d16;
    tensor.d16 = temp;
    r16.write(pool_id, temp);
    
    r17.read(temp, pool_id);
    temp = temp + tensor.d17;
    tensor.d17 = temp;
    r17.write(pool_id, temp);
    
    r18.read(temp, pool_id);
    temp = temp + tensor.d18;
    tensor.d18 = temp;
    r18.write(pool_id, temp);
    
    r19.read(temp, pool_id);
    temp = temp + tensor.d19;
    tensor.d19 = temp;
    r19.write(pool_id, temp);
    
    r20.read(temp, pool_id);
    temp = temp + tensor.d20;
    tensor.d20 = temp;
    r20.write(pool_id, temp);

    r21.read(temp, pool_id);
    temp = temp + tensor.d21;
    tensor.d21 = temp;
    r21.write(pool_id, temp);

    r22.read(temp, pool_id);
    temp = temp + tensor.d22;
    tensor.d22 = temp;
    r22.write(pool_id, temp);
    
    r23.read(temp, pool_id);
    temp = temp + tensor.d23;
    tensor.d23 = temp;
    r23.write(pool_id, temp);
    
    r24.read(temp, pool_id);
    temp = temp + tensor.d24;
    tensor.d24 = temp;
    r24.write(pool_id, temp);
    
    r25.read(temp, pool_id);
    temp = temp + tensor.d25;
    tensor.d25 = temp;
    r25.write(pool_id, temp);
    
    r26.read(temp, pool_id);
    temp = temp + tensor.d26;
    tensor.d26 = temp;
    r26.write(pool_id, temp);
    
    r27.read(temp, pool_id);
    temp = temp + tensor.d27;
    tensor.d27 = temp;
    r27.write(pool_id, temp);
    
    r28.read(temp, pool_id);
    temp = temp + tensor.d28;
    tensor.d28 = temp;
    r28.write(pool_id, temp);
    
    r29.read(temp, pool_id);
    temp = temp + tensor.d29;
    tensor.d29 = temp;
    r29.write(pool_id, temp);
    
    r30.read(temp, pool_id);
    temp = temp + tensor.d30;
    tensor.d30 = temp;
    r30.write(pool_id, temp);
    
    r31.read(temp, pool_id);
    temp = temp + tensor.d31;
    tensor.d31 = temp;
    r31.write(pool_id, temp);
    // loop end
  }

  action reset(){
    r0.write(pool_id, 0);
    r1.write(pool_id, 0);
    r2.write(pool_id, 0);
    r3.write(pool_id, 0);
    r4.write(pool_id, 0);
    r5.write(pool_id, 0);
    r6.write(pool_id, 0);
    r7.write(pool_id, 0);
    r8.write(pool_id, 0);
    r9.write(pool_id, 0);
    r10.write(pool_id, 0);
    r11.write(pool_id, 0);
    r12.write(pool_id, 0);
    r13.write(pool_id, 0);
    r14.write(pool_id, 0);
    r15.write(pool_id, 0);
    r16.write(pool_id, 0);
    r17.write(pool_id, 0);
    r18.write(pool_id, 0);
    r19.write(pool_id, 0);
    r20.write(pool_id, 0);
    r21.write(pool_id, 0);
    r22.write(pool_id, 0);
    r23.write(pool_id, 0);
    r24.write(pool_id, 0);
    r25.write(pool_id, 0);
    r26.write(pool_id, 0);
    r27.write(pool_id, 0);
    r28.write(pool_id, 0);
    r29.write(pool_id, 0);
    r30.write(pool_id, 0);
    r31.write(pool_id, 0);
  }

  apply {
    if(is_reset_action) {
      reset();
    }else{
      aggregate();
    }
  }
}
