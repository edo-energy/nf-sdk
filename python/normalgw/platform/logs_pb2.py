# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: normalgw/platform/logs.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='normalgw/platform/logs.proto',
  package='normalgw.platform',
  syntax='proto3',
  serialized_options=b'Z\'github.com/stevedh/gobac/proto/platform',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x1cnormalgw/platform/logs.proto\x12\x11normalgw.platform\"P\n\rGetLogRequest\x12\x11\n\tcomponent\x18\x01 \x01(\t\x12\x0e\n\x06\x66ilter\x18\x02 \x01(\t\x12\x0e\n\x06\x66ollow\x18\x03 \x01(\x08\x12\x0c\n\x04tail\x18\x04 \x01(\r\"\x1a\n\nLogMessage\x12\x0c\n\x04line\x18\x01 \x01(\t2T\n\x04Logs\x12L\n\x07GetLogs\x12 .normalgw.platform.GetLogRequest\x1a\x1d.normalgw.platform.LogMessage0\x01\x42)Z\'github.com/stevedh/gobac/proto/platformb\x06proto3'
)




_GETLOGREQUEST = _descriptor.Descriptor(
  name='GetLogRequest',
  full_name='normalgw.platform.GetLogRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='component', full_name='normalgw.platform.GetLogRequest.component', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='filter', full_name='normalgw.platform.GetLogRequest.filter', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='follow', full_name='normalgw.platform.GetLogRequest.follow', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='tail', full_name='normalgw.platform.GetLogRequest.tail', index=3,
      number=4, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=51,
  serialized_end=131,
)


_LOGMESSAGE = _descriptor.Descriptor(
  name='LogMessage',
  full_name='normalgw.platform.LogMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='line', full_name='normalgw.platform.LogMessage.line', index=0,
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
  serialized_start=133,
  serialized_end=159,
)

DESCRIPTOR.message_types_by_name['GetLogRequest'] = _GETLOGREQUEST
DESCRIPTOR.message_types_by_name['LogMessage'] = _LOGMESSAGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

GetLogRequest = _reflection.GeneratedProtocolMessageType('GetLogRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETLOGREQUEST,
  '__module__' : 'normalgw.platform.logs_pb2'
  # @@protoc_insertion_point(class_scope:normalgw.platform.GetLogRequest)
  })
_sym_db.RegisterMessage(GetLogRequest)

LogMessage = _reflection.GeneratedProtocolMessageType('LogMessage', (_message.Message,), {
  'DESCRIPTOR' : _LOGMESSAGE,
  '__module__' : 'normalgw.platform.logs_pb2'
  # @@protoc_insertion_point(class_scope:normalgw.platform.LogMessage)
  })
_sym_db.RegisterMessage(LogMessage)


DESCRIPTOR._options = None

_LOGS = _descriptor.ServiceDescriptor(
  name='Logs',
  full_name='normalgw.platform.Logs',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=161,
  serialized_end=245,
  methods=[
  _descriptor.MethodDescriptor(
    name='GetLogs',
    full_name='normalgw.platform.Logs.GetLogs',
    index=0,
    containing_service=None,
    input_type=_GETLOGREQUEST,
    output_type=_LOGMESSAGE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_LOGS)

DESCRIPTOR.services_by_name['Logs'] = _LOGS

# @@protoc_insertion_point(module_scope)
