from concurrent import futures
import io_pb2_grpc
from google.protobuf.empty_pb2 import Empty
from io_pb2 import Retransmission, PacketLoss
import numpy as np
import grpc
import io_pb2_grpc
import threading
from packet import elemenet_per_packet


class SwitchmlIOServicer(io_pb2_grpc.SwitchmlIOServicer):
    def __init__(self, node) -> None:
        super().__init__()
        self.node = node

    def SendBarrier(self, request, context):
        # TODO
        return Empty()

    def Retransmission(self, request: Retransmission.Request, context):
        job = self.node.rx_jobs.get((request.tensor_id, request.node_id))
        for slice in request.data.items():
            packet_num, data = slice
            offset = packet_num * elemenet_per_packet
            job.tensor[offset: offset +
                       elemenet_per_packet] = np.frombuffer(data, dtype=np.int32)
            job.bitmap[int(offset / elemenet_per_packet)] = 1
        job.finish()
        return Empty()

    def ReadMissingSlice(self, request: PacketLoss.Request, context):
        job = self.node.rx_jobs.get((request.tensor_id, request.node_id))
        missing_packet_list = np.where(job.bitmap == 0)[0]
        return PacketLoss.Response(missing_packet_list=missing_packet_list)


class GrpcServer:
    def __init__(self, node):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        io_pb2_grpc.add_SwitchmlIOServicer_to_server(
            SwitchmlIOServicer(node),
            self.server
        )
        self.server.add_insecure_port(
            '0.0.0.0:%d' % (node.options["rpc_port"]))
        self.server.start()
        threading.Thread(target=self.server.wait_for_termination).start()

    def stop(self):
        self.server.stop(grace=None)
