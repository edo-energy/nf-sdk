# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: normalgw/platform/config.proto

from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='normalgw/platform/config.proto',
  package='normalgw.platform',
  syntax='proto3',
  serialized_options=b'Z\'github.com/stevedh/gobac/proto/platform',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x1enormalgw/platform/config.proto\x12\x11normalgw.platform\"V\n\x14NetworkInterfaceList\x12>\n\ninterfaces\x18\x01 \x03(\x0b\x32*.normalgw.platform.NetworkInterfaceDetails\"\x91\x01\n\x17NetworkInterfaceDetails\x12\x0f\n\x07\x61ttr_id\x18\x01 \x01(\x04\x12\x16\n\x0einterface_name\x18\x02 \x01(\t\x12\x11\n\tipv4_addr\x18\x03 \x01(\x0c\x12\x0c\n\x04mask\x18\x04 \x01(\r\x12\x1a\n\x12ipv4_default_route\x18\x05 \x01(\x0c\x12\x10\n\x08ipv4_dns\x18\x06 \x03(\x0c\"|\n\x14ServiceStatusDetails\x12\x0c\n\x04name\x18\x01 \x03(\t\x12\x0f\n\x07\x64\x65tails\x18\x02 \x03(\t\x12\x30\n\x06status\x18\x03 \x03(\x0e\x32 .normalgw.platform.ServiceStatus\x12\x13\n\x0bstatus_time\x18\x04 \x03(\x04\"\x1d\n\x1bGetSystemInformationRequest\".\n\x19GetSystemInformationReply\x12\x11\n\tsite_name\x18\x01 \x01(\t*.\n\rServiceStatus\x12\x08\n\x04\x44OWN\x10\x00\x12\x06\n\x02UP\x10\x01\x12\x0b\n\x07UNKNOWN\x10\x03\x32\x85\x01\n\rConfiguration\x12t\n\x14GetSystemInformation\x12..normalgw.platform.GetSystemInformationRequest\x1a,.normalgw.platform.GetSystemInformationReplyB)Z\'github.com/stevedh/gobac/proto/platformb\x06proto3'
)

_SERVICESTATUS = _descriptor.EnumDescriptor(
  name='ServiceStatus',
  full_name='normalgw.platform.ServiceStatus',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='DOWN', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='UP', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN', index=2, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=494,
  serialized_end=540,
)
_sym_db.RegisterEnumDescriptor(_SERVICESTATUS)

ServiceStatus = enum_type_wrapper.EnumTypeWrapper(_SERVICESTATUS)
DOWN = 0
UP = 1
UNKNOWN = 3



_NETWORKINTERFACELIST = _descriptor.Descriptor(
  name='NetworkInterfaceList',
  full_name='normalgw.platform.NetworkInterfaceList',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='interfaces', full_name='normalgw.platform.NetworkInterfaceList.interfaces', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=53,
  serialized_end=139,
)


_NETWORKINTERFACEDETAILS = _descriptor.Descriptor(
  name='NetworkInterfaceDetails',
  full_name='normalgw.platform.NetworkInterfaceDetails',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='attr_id', full_name='normalgw.platform.NetworkInterfaceDetails.attr_id', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='interface_name', full_name='normalgw.platform.NetworkInterfaceDetails.interface_name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='ipv4_addr', full_name='normalgw.platform.NetworkInterfaceDetails.ipv4_addr', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='mask', full_name='normalgw.platform.NetworkInterfaceDetails.mask', index=3,
      number=4, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='ipv4_default_route', full_name='normalgw.platform.NetworkInterfaceDetails.ipv4_default_route', index=4,
      number=5, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='ipv4_dns', full_name='normalgw.platform.NetworkInterfaceDetails.ipv4_dns', index=5,
      number=6, type=12, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=142,
  serialized_end=287,
)


_SERVICESTATUSDETAILS = _descriptor.Descriptor(
  name='ServiceStatusDetails',
  full_name='normalgw.platform.ServiceStatusDetails',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='normalgw.platform.ServiceStatusDetails.name', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='details', full_name='normalgw.platform.ServiceStatusDetails.details', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='status', full_name='normalgw.platform.ServiceStatusDetails.status', index=2,
      number=3, type=14, cpp_type=8, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='status_time', full_name='normalgw.platform.ServiceStatusDetails.status_time', index=3,
      number=4, type=4, cpp_type=4, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=289,
  serialized_end=413,
)


_GETSYSTEMINFORMATIONREQUEST = _descriptor.Descriptor(
  name='GetSystemInformationRequest',
  full_name='normalgw.platform.GetSystemInformationRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=415,
  serialized_end=444,
)


_GETSYSTEMINFORMATIONREPLY = _descriptor.Descriptor(
  name='GetSystemInformationReply',
  full_name='normalgw.platform.GetSystemInformationReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='site_name', full_name='normalgw.platform.GetSystemInformationReply.site_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=446,
  serialized_end=492,
)

_NETWORKINTERFACELIST.fields_by_name['interfaces'].message_type = _NETWORKINTERFACEDETAILS
_SERVICESTATUSDETAILS.fields_by_name['status'].enum_type = _SERVICESTATUS
DESCRIPTOR.message_types_by_name['NetworkInterfaceList'] = _NETWORKINTERFACELIST
DESCRIPTOR.message_types_by_name['NetworkInterfaceDetails'] = _NETWORKINTERFACEDETAILS
DESCRIPTOR.message_types_by_name['ServiceStatusDetails'] = _SERVICESTATUSDETAILS
DESCRIPTOR.message_types_by_name['GetSystemInformationRequest'] = _GETSYSTEMINFORMATIONREQUEST
DESCRIPTOR.message_types_by_name['GetSystemInformationReply'] = _GETSYSTEMINFORMATIONREPLY
DESCRIPTOR.enum_types_by_name['ServiceStatus'] = _SERVICESTATUS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

NetworkInterfaceList = _reflection.GeneratedProtocolMessageType('NetworkInterfaceList', (_message.Message,), {
  'DESCRIPTOR' : _NETWORKINTERFACELIST,
  '__module__' : 'normalgw.platform.config_pb2'
  # @@protoc_insertion_point(class_scope:normalgw.platform.NetworkInterfaceList)
  })
_sym_db.RegisterMessage(NetworkInterfaceList)

NetworkInterfaceDetails = _reflection.GeneratedProtocolMessageType('NetworkInterfaceDetails', (_message.Message,), {
  'DESCRIPTOR' : _NETWORKINTERFACEDETAILS,
  '__module__' : 'normalgw.platform.config_pb2'
  # @@protoc_insertion_point(class_scope:normalgw.platform.NetworkInterfaceDetails)
  })
_sym_db.RegisterMessage(NetworkInterfaceDetails)

ServiceStatusDetails = _reflection.GeneratedProtocolMessageType('ServiceStatusDetails', (_message.Message,), {
  'DESCRIPTOR' : _SERVICESTATUSDETAILS,
  '__module__' : 'normalgw.platform.config_pb2'
  # @@protoc_insertion_point(class_scope:normalgw.platform.ServiceStatusDetails)
  })
_sym_db.RegisterMessage(ServiceStatusDetails)

GetSystemInformationRequest = _reflection.GeneratedProtocolMessageType('GetSystemInformationRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETSYSTEMINFORMATIONREQUEST,
  '__module__' : 'normalgw.platform.config_pb2'
  # @@protoc_insertion_point(class_scope:normalgw.platform.GetSystemInformationRequest)
  })
_sym_db.RegisterMessage(GetSystemInformationRequest)

GetSystemInformationReply = _reflection.GeneratedProtocolMessageType('GetSystemInformationReply', (_message.Message,), {
  'DESCRIPTOR' : _GETSYSTEMINFORMATIONREPLY,
  '__module__' : 'normalgw.platform.config_pb2'
  # @@protoc_insertion_point(class_scope:normalgw.platform.GetSystemInformationReply)
  })
_sym_db.RegisterMessage(GetSystemInformationReply)


DESCRIPTOR._options = None

_CONFIGURATION = _descriptor.ServiceDescriptor(
  name='Configuration',
  full_name='normalgw.platform.Configuration',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=543,
  serialized_end=676,
  methods=[
  _descriptor.MethodDescriptor(
    name='GetSystemInformation',
    full_name='normalgw.platform.Configuration.GetSystemInformation',
    index=0,
    containing_service=None,
    input_type=_GETSYSTEMINFORMATIONREQUEST,
    output_type=_GETSYSTEMINFORMATIONREPLY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_CONFIGURATION)

DESCRIPTOR.services_by_name['Configuration'] = _CONFIGURATION

# @@protoc_insertion_point(module_scope)