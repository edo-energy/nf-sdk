// source: normalgw/platform/logs.proto
/**
 * @fileoverview
 * @enhanceable
 * @suppress {messageConventions} JS Compiler reports an error if a variable or
 *     field starts with 'MSG_' and isn't a translatable message.
 * @public
 */
// GENERATED CODE -- DO NOT EDIT!

var jspb = require('google-protobuf');
var goog = jspb;
var global = Function('return this')();

goog.exportSymbol('proto.normalgw.platform.GetLogRequest', null, global);
goog.exportSymbol('proto.normalgw.platform.LogMessage', null, global);
/**
 * Generated by JsPbCodeGenerator.
 * @param {Array=} opt_data Optional initial data array, typically from a
 * server response, or constructed directly in Javascript. The array is used
 * in place and becomes part of the constructed object. It is not cloned.
 * If no data is provided, the constructed object will be empty, but still
 * valid.
 * @extends {jspb.Message}
 * @constructor
 */
proto.normalgw.platform.GetLogRequest = function(opt_data) {
  jspb.Message.initialize(this, opt_data, 0, -1, null, null);
};
goog.inherits(proto.normalgw.platform.GetLogRequest, jspb.Message);
if (goog.DEBUG && !COMPILED) {
  /**
   * @public
   * @override
   */
  proto.normalgw.platform.GetLogRequest.displayName = 'proto.normalgw.platform.GetLogRequest';
}
/**
 * Generated by JsPbCodeGenerator.
 * @param {Array=} opt_data Optional initial data array, typically from a
 * server response, or constructed directly in Javascript. The array is used
 * in place and becomes part of the constructed object. It is not cloned.
 * If no data is provided, the constructed object will be empty, but still
 * valid.
 * @extends {jspb.Message}
 * @constructor
 */
proto.normalgw.platform.LogMessage = function(opt_data) {
  jspb.Message.initialize(this, opt_data, 0, -1, null, null);
};
goog.inherits(proto.normalgw.platform.LogMessage, jspb.Message);
if (goog.DEBUG && !COMPILED) {
  /**
   * @public
   * @override
   */
  proto.normalgw.platform.LogMessage.displayName = 'proto.normalgw.platform.LogMessage';
}



if (jspb.Message.GENERATE_TO_OBJECT) {
/**
 * Creates an object representation of this proto.
 * Field names that are reserved in JavaScript and will be renamed to pb_name.
 * Optional fields that are not set will be set to undefined.
 * To access a reserved field use, foo.pb_<name>, eg, foo.pb_default.
 * For the list of reserved names please see:
 *     net/proto2/compiler/js/internal/generator.cc#kKeyword.
 * @param {boolean=} opt_includeInstance Deprecated. whether to include the
 *     JSPB instance for transitional soy proto support:
 *     http://goto/soy-param-migration
 * @return {!Object}
 */
proto.normalgw.platform.GetLogRequest.prototype.toObject = function(opt_includeInstance) {
  return proto.normalgw.platform.GetLogRequest.toObject(opt_includeInstance, this);
};


/**
 * Static version of the {@see toObject} method.
 * @param {boolean|undefined} includeInstance Deprecated. Whether to include
 *     the JSPB instance for transitional soy proto support:
 *     http://goto/soy-param-migration
 * @param {!proto.normalgw.platform.GetLogRequest} msg The msg instance to transform.
 * @return {!Object}
 * @suppress {unusedLocalVariables} f is only used for nested messages
 */
proto.normalgw.platform.GetLogRequest.toObject = function(includeInstance, msg) {
  var f, obj = {
    component: jspb.Message.getFieldWithDefault(msg, 1, ""),
    filter: jspb.Message.getFieldWithDefault(msg, 2, ""),
    follow: jspb.Message.getBooleanFieldWithDefault(msg, 3, false),
    tail: jspb.Message.getFieldWithDefault(msg, 4, 0)
  };

  if (includeInstance) {
    obj.$jspbMessageInstance = msg;
  }
  return obj;
};
}


/**
 * Deserializes binary data (in protobuf wire format).
 * @param {jspb.ByteSource} bytes The bytes to deserialize.
 * @return {!proto.normalgw.platform.GetLogRequest}
 */
proto.normalgw.platform.GetLogRequest.deserializeBinary = function(bytes) {
  var reader = new jspb.BinaryReader(bytes);
  var msg = new proto.normalgw.platform.GetLogRequest;
  return proto.normalgw.platform.GetLogRequest.deserializeBinaryFromReader(msg, reader);
};


/**
 * Deserializes binary data (in protobuf wire format) from the
 * given reader into the given message object.
 * @param {!proto.normalgw.platform.GetLogRequest} msg The message object to deserialize into.
 * @param {!jspb.BinaryReader} reader The BinaryReader to use.
 * @return {!proto.normalgw.platform.GetLogRequest}
 */
proto.normalgw.platform.GetLogRequest.deserializeBinaryFromReader = function(msg, reader) {
  while (reader.nextField()) {
    if (reader.isEndGroup()) {
      break;
    }
    var field = reader.getFieldNumber();
    switch (field) {
    case 1:
      var value = /** @type {string} */ (reader.readString());
      msg.setComponent(value);
      break;
    case 2:
      var value = /** @type {string} */ (reader.readString());
      msg.setFilter(value);
      break;
    case 3:
      var value = /** @type {boolean} */ (reader.readBool());
      msg.setFollow(value);
      break;
    case 4:
      var value = /** @type {number} */ (reader.readUint32());
      msg.setTail(value);
      break;
    default:
      reader.skipField();
      break;
    }
  }
  return msg;
};


/**
 * Serializes the message to binary data (in protobuf wire format).
 * @return {!Uint8Array}
 */
proto.normalgw.platform.GetLogRequest.prototype.serializeBinary = function() {
  var writer = new jspb.BinaryWriter();
  proto.normalgw.platform.GetLogRequest.serializeBinaryToWriter(this, writer);
  return writer.getResultBuffer();
};


/**
 * Serializes the given message to binary data (in protobuf wire
 * format), writing to the given BinaryWriter.
 * @param {!proto.normalgw.platform.GetLogRequest} message
 * @param {!jspb.BinaryWriter} writer
 * @suppress {unusedLocalVariables} f is only used for nested messages
 */
proto.normalgw.platform.GetLogRequest.serializeBinaryToWriter = function(message, writer) {
  var f = undefined;
  f = message.getComponent();
  if (f.length > 0) {
    writer.writeString(
      1,
      f
    );
  }
  f = message.getFilter();
  if (f.length > 0) {
    writer.writeString(
      2,
      f
    );
  }
  f = message.getFollow();
  if (f) {
    writer.writeBool(
      3,
      f
    );
  }
  f = message.getTail();
  if (f !== 0) {
    writer.writeUint32(
      4,
      f
    );
  }
};


/**
 * optional string component = 1;
 * @return {string}
 */
proto.normalgw.platform.GetLogRequest.prototype.getComponent = function() {
  return /** @type {string} */ (jspb.Message.getFieldWithDefault(this, 1, ""));
};


/**
 * @param {string} value
 * @return {!proto.normalgw.platform.GetLogRequest} returns this
 */
proto.normalgw.platform.GetLogRequest.prototype.setComponent = function(value) {
  return jspb.Message.setProto3StringField(this, 1, value);
};


/**
 * optional string filter = 2;
 * @return {string}
 */
proto.normalgw.platform.GetLogRequest.prototype.getFilter = function() {
  return /** @type {string} */ (jspb.Message.getFieldWithDefault(this, 2, ""));
};


/**
 * @param {string} value
 * @return {!proto.normalgw.platform.GetLogRequest} returns this
 */
proto.normalgw.platform.GetLogRequest.prototype.setFilter = function(value) {
  return jspb.Message.setProto3StringField(this, 2, value);
};


/**
 * optional bool follow = 3;
 * @return {boolean}
 */
proto.normalgw.platform.GetLogRequest.prototype.getFollow = function() {
  return /** @type {boolean} */ (jspb.Message.getBooleanFieldWithDefault(this, 3, false));
};


/**
 * @param {boolean} value
 * @return {!proto.normalgw.platform.GetLogRequest} returns this
 */
proto.normalgw.platform.GetLogRequest.prototype.setFollow = function(value) {
  return jspb.Message.setProto3BooleanField(this, 3, value);
};


/**
 * optional uint32 tail = 4;
 * @return {number}
 */
proto.normalgw.platform.GetLogRequest.prototype.getTail = function() {
  return /** @type {number} */ (jspb.Message.getFieldWithDefault(this, 4, 0));
};


/**
 * @param {number} value
 * @return {!proto.normalgw.platform.GetLogRequest} returns this
 */
proto.normalgw.platform.GetLogRequest.prototype.setTail = function(value) {
  return jspb.Message.setProto3IntField(this, 4, value);
};





if (jspb.Message.GENERATE_TO_OBJECT) {
/**
 * Creates an object representation of this proto.
 * Field names that are reserved in JavaScript and will be renamed to pb_name.
 * Optional fields that are not set will be set to undefined.
 * To access a reserved field use, foo.pb_<name>, eg, foo.pb_default.
 * For the list of reserved names please see:
 *     net/proto2/compiler/js/internal/generator.cc#kKeyword.
 * @param {boolean=} opt_includeInstance Deprecated. whether to include the
 *     JSPB instance for transitional soy proto support:
 *     http://goto/soy-param-migration
 * @return {!Object}
 */
proto.normalgw.platform.LogMessage.prototype.toObject = function(opt_includeInstance) {
  return proto.normalgw.platform.LogMessage.toObject(opt_includeInstance, this);
};


/**
 * Static version of the {@see toObject} method.
 * @param {boolean|undefined} includeInstance Deprecated. Whether to include
 *     the JSPB instance for transitional soy proto support:
 *     http://goto/soy-param-migration
 * @param {!proto.normalgw.platform.LogMessage} msg The msg instance to transform.
 * @return {!Object}
 * @suppress {unusedLocalVariables} f is only used for nested messages
 */
proto.normalgw.platform.LogMessage.toObject = function(includeInstance, msg) {
  var f, obj = {
    line: jspb.Message.getFieldWithDefault(msg, 1, "")
  };

  if (includeInstance) {
    obj.$jspbMessageInstance = msg;
  }
  return obj;
};
}


/**
 * Deserializes binary data (in protobuf wire format).
 * @param {jspb.ByteSource} bytes The bytes to deserialize.
 * @return {!proto.normalgw.platform.LogMessage}
 */
proto.normalgw.platform.LogMessage.deserializeBinary = function(bytes) {
  var reader = new jspb.BinaryReader(bytes);
  var msg = new proto.normalgw.platform.LogMessage;
  return proto.normalgw.platform.LogMessage.deserializeBinaryFromReader(msg, reader);
};


/**
 * Deserializes binary data (in protobuf wire format) from the
 * given reader into the given message object.
 * @param {!proto.normalgw.platform.LogMessage} msg The message object to deserialize into.
 * @param {!jspb.BinaryReader} reader The BinaryReader to use.
 * @return {!proto.normalgw.platform.LogMessage}
 */
proto.normalgw.platform.LogMessage.deserializeBinaryFromReader = function(msg, reader) {
  while (reader.nextField()) {
    if (reader.isEndGroup()) {
      break;
    }
    var field = reader.getFieldNumber();
    switch (field) {
    case 1:
      var value = /** @type {string} */ (reader.readString());
      msg.setLine(value);
      break;
    default:
      reader.skipField();
      break;
    }
  }
  return msg;
};


/**
 * Serializes the message to binary data (in protobuf wire format).
 * @return {!Uint8Array}
 */
proto.normalgw.platform.LogMessage.prototype.serializeBinary = function() {
  var writer = new jspb.BinaryWriter();
  proto.normalgw.platform.LogMessage.serializeBinaryToWriter(this, writer);
  return writer.getResultBuffer();
};


/**
 * Serializes the given message to binary data (in protobuf wire
 * format), writing to the given BinaryWriter.
 * @param {!proto.normalgw.platform.LogMessage} message
 * @param {!jspb.BinaryWriter} writer
 * @suppress {unusedLocalVariables} f is only used for nested messages
 */
proto.normalgw.platform.LogMessage.serializeBinaryToWriter = function(message, writer) {
  var f = undefined;
  f = message.getLine();
  if (f.length > 0) {
    writer.writeString(
      1,
      f
    );
  }
};


/**
 * optional string line = 1;
 * @return {string}
 */
proto.normalgw.platform.LogMessage.prototype.getLine = function() {
  return /** @type {string} */ (jspb.Message.getFieldWithDefault(this, 1, ""));
};


/**
 * @param {string} value
 * @return {!proto.normalgw.platform.LogMessage} returns this
 */
proto.normalgw.platform.LogMessage.prototype.setLine = function(value) {
  return jspb.Message.setProto3StringField(this, 1, value);
};


goog.object.extend(exports, proto.normalgw.platform);