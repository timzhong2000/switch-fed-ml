from packet import Packet
import numpy as np
import threading
import math
from packet import elemenet_per_packet

# 接收任务
class Job:
    def __init__(self, key: tuple, tensor: np.ndarray, worker_number: int = 1):
        self.tensor = tensor
        self.total_packet_num = math.ceil(tensor.size / elemenet_per_packet)
        self.bitmap = np.zeros(shape=(self.total_packet_num), dtype=np.int8)
        # 任务完成时解锁
        self._lock = threading.Lock()
        self._lock.acquire()
        self.remain_worker_number = worker_number

    def finish(self):
        self.remain_worker_number -= 1
        if self.remain_worker_number == 0:
            self._lock.release()

    def wait_until_job_finish(self):
        self._lock.acquire()
        self._lock.release()

    def handle_packet(self, pkt: Packet):
        offset = pkt.segment_id * elemenet_per_packet
        self.tensor[offset: offset + elemenet_per_packet] = pkt.tensor
        self.bitmap[int(offset / elemenet_per_packet)] = 1

    def handle_retransmission_packet(self, pkt: Packet):
        offset = pkt.segment_id * elemenet_per_packet
        self.tensor[offset: offset + elemenet_per_packet] += pkt.tensor
        self.bitmap[int(offset / elemenet_per_packet)] += 1