from packet import Packet
import numpy as np
import threading
import math
from packet import elemenet_per_packet


class Job:
    def __init__(self, key: tuple, tensor: np.ndarray):
        self.tensor = tensor
        self.total_packet_num = math.ceil(tensor.size / elemenet_per_packet)
        self.bitmap = np.zeros(shape=(self.total_packet_num), dtype=np.int8)
        # 任务完成时解锁
        self._lock = threading.Lock()
        self._lock.acquire()

    def finish(self):
        self._lock.release()

    def wait_until_job_finish(self):
        self._lock.acquire()
        self._lock.release()

    def handle_packet(self, pkt: Packet):
        offser = pkt.packet_num * elemenet_per_packet
        self.tensor[offser: offser + elemenet_per_packet] = pkt.tensor
        self.bitmap[int(offser / elemenet_per_packet)] = 1
