# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: io.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x08io.proto\"J\n\x0eRetransmission\x1a\x38\n\x07Request\x12\x0e\n\x06job_id\x18\x01 \x01(\x05\x12\x0f\n\x07node_id\x18\x02 \x01(\x05\x12\x0c\n\x04\x64\x61ta\x18\x63 \x03(\x0c\"t\n\nPacketLoss\x1a=\n\x07Request\x12\x0e\n\x06job_id\x18\x01 \x01(\x05\x12\x0f\n\x07node_id\x18\x02 \x01(\x05\x12\x11\n\trange_end\x18\x03 \x01(\x05\x1a\'\n\x08Response\x12\x1b\n\x13missing_packet_list\x18\x01 \x03(\x05\"\x06\n\x04Null2}\n\nSwitchmlIO\x12\x30\n\x0eRetransmission\x12\x17.Retransmission.Request\x1a\x05.Null\x12=\n\x10ReadMissingSlice\x12\x13.PacketLoss.Request\x1a\x14.PacketLoss.Responseb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'io_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _RETRANSMISSION._serialized_start=12
  _RETRANSMISSION._serialized_end=86
  _RETRANSMISSION_REQUEST._serialized_start=30
  _RETRANSMISSION_REQUEST._serialized_end=86
  _PACKETLOSS._serialized_start=88
  _PACKETLOSS._serialized_end=204
  _PACKETLOSS_REQUEST._serialized_start=102
  _PACKETLOSS_REQUEST._serialized_end=163
  _PACKETLOSS_RESPONSE._serialized_start=165
  _PACKETLOSS_RESPONSE._serialized_end=204
  _NULL._serialized_start=206
  _NULL._serialized_end=212
  _SWITCHMLIO._serialized_start=214
  _SWITCHMLIO._serialized_end=339
# @@protoc_insertion_point(module_scope)
