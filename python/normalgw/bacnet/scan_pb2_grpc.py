# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from normalgw.bacnet import scan_pb2 as normalgw_dot_bacnet_dot_scan__pb2


class ScanStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetJobs = channel.unary_unary(
                '/normalgw.bacnet.Scan/GetJobs',
                request_serializer=normalgw_dot_bacnet_dot_scan__pb2.GetJobRequest.SerializeToString,
                response_deserializer=normalgw_dot_bacnet_dot_scan__pb2.GetJobReply.FromString,
                )
        self.StartJob = channel.unary_unary(
                '/normalgw.bacnet.Scan/StartJob',
                request_serializer=normalgw_dot_bacnet_dot_scan__pb2.StartJobRequest.SerializeToString,
                response_deserializer=normalgw_dot_bacnet_dot_scan__pb2.ScanJob.FromString,
                )
        self.RestartJobs = channel.unary_unary(
                '/normalgw.bacnet.Scan/RestartJobs',
                request_serializer=normalgw_dot_bacnet_dot_scan__pb2.RestartJobsRequest.SerializeToString,
                response_deserializer=normalgw_dot_bacnet_dot_scan__pb2.RestartJobsReply.FromString,
                )
        self.ImportJob = channel.unary_unary(
                '/normalgw.bacnet.Scan/ImportJob',
                request_serializer=normalgw_dot_bacnet_dot_scan__pb2.ImportJobRequest.SerializeToString,
                response_deserializer=normalgw_dot_bacnet_dot_scan__pb2.ImportJobReply.FromString,
                )
        self.ObserveJobUpdates = channel.unary_stream(
                '/normalgw.bacnet.Scan/ObserveJobUpdates',
                request_serializer=normalgw_dot_bacnet_dot_scan__pb2.ObserveJobUpdatesRequest.SerializeToString,
                response_deserializer=normalgw_dot_bacnet_dot_scan__pb2.ObserveJobUpdatesReply.FromString,
                )
        self.GetScanDeltas = channel.unary_stream(
                '/normalgw.bacnet.Scan/GetScanDeltas',
                request_serializer=normalgw_dot_bacnet_dot_scan__pb2.GetScanDeltaRequest.SerializeToString,
                response_deserializer=normalgw_dot_bacnet_dot_scan__pb2.GetScanDeltaReply.FromString,
                )


class ScanServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetJobs(self, request, context):
        """GetJobs

        Retrievae jobs which have been submitted by StartJob

        The StartJob request message allows a client to sort, filter and
        paginate the jobs based on Job ID.

        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StartJob(self, request, context):
        """StartJob

        Add a new job to the Job queue.  Only one of the device, object,
        or network scans must be specified.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestartJobs(self, request, context):
        """RestartJobs

        Restart jobs is a simple way to resubmit jobs which may have failed / been canceled.

        A new job is created with the same arguments as the original job had.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ImportJob(self, request, context):
        """ImportJob

        Import an already-completed job into the Graph database.

        Normally, you would import jobs using auto_import = True on a
        job.  However if a job was not imported so that it could be
        reviewed, you may want to just import the job.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ObserveJobUpdates(self, request, context):
        """ObserveJobUpdates

        Listen to a stream of completed jobs.

        This interface returns a stream of jobs which have 
        ended (either succeded or failed).  This allows downstream clients to synchronize object
        databases with this system without missing any records.

        The call returns onces all available scans have been sent.

        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetScanDeltas(self, request, context):
        """GetScanDeltas 

        Get a stream of object scan deltas.

        This interface returns a stream of scan results with the changes
        (created/updated/deleted) devices and objects provided.  This
        makes it easy to build visualizations and other interfaces which
        track the network state over time.  The stream is closed after
        all scans have been sent.

        The first record for a device / object is guaranteed to be a
        create so you can replicate the current state of the network by
        replaying these deltas.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ScanServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetJobs': grpc.unary_unary_rpc_method_handler(
                    servicer.GetJobs,
                    request_deserializer=normalgw_dot_bacnet_dot_scan__pb2.GetJobRequest.FromString,
                    response_serializer=normalgw_dot_bacnet_dot_scan__pb2.GetJobReply.SerializeToString,
            ),
            'StartJob': grpc.unary_unary_rpc_method_handler(
                    servicer.StartJob,
                    request_deserializer=normalgw_dot_bacnet_dot_scan__pb2.StartJobRequest.FromString,
                    response_serializer=normalgw_dot_bacnet_dot_scan__pb2.ScanJob.SerializeToString,
            ),
            'RestartJobs': grpc.unary_unary_rpc_method_handler(
                    servicer.RestartJobs,
                    request_deserializer=normalgw_dot_bacnet_dot_scan__pb2.RestartJobsRequest.FromString,
                    response_serializer=normalgw_dot_bacnet_dot_scan__pb2.RestartJobsReply.SerializeToString,
            ),
            'ImportJob': grpc.unary_unary_rpc_method_handler(
                    servicer.ImportJob,
                    request_deserializer=normalgw_dot_bacnet_dot_scan__pb2.ImportJobRequest.FromString,
                    response_serializer=normalgw_dot_bacnet_dot_scan__pb2.ImportJobReply.SerializeToString,
            ),
            'ObserveJobUpdates': grpc.unary_stream_rpc_method_handler(
                    servicer.ObserveJobUpdates,
                    request_deserializer=normalgw_dot_bacnet_dot_scan__pb2.ObserveJobUpdatesRequest.FromString,
                    response_serializer=normalgw_dot_bacnet_dot_scan__pb2.ObserveJobUpdatesReply.SerializeToString,
            ),
            'GetScanDeltas': grpc.unary_stream_rpc_method_handler(
                    servicer.GetScanDeltas,
                    request_deserializer=normalgw_dot_bacnet_dot_scan__pb2.GetScanDeltaRequest.FromString,
                    response_serializer=normalgw_dot_bacnet_dot_scan__pb2.GetScanDeltaReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'normalgw.bacnet.Scan', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Scan(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetJobs(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/normalgw.bacnet.Scan/GetJobs',
            normalgw_dot_bacnet_dot_scan__pb2.GetJobRequest.SerializeToString,
            normalgw_dot_bacnet_dot_scan__pb2.GetJobReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def StartJob(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/normalgw.bacnet.Scan/StartJob',
            normalgw_dot_bacnet_dot_scan__pb2.StartJobRequest.SerializeToString,
            normalgw_dot_bacnet_dot_scan__pb2.ScanJob.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RestartJobs(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/normalgw.bacnet.Scan/RestartJobs',
            normalgw_dot_bacnet_dot_scan__pb2.RestartJobsRequest.SerializeToString,
            normalgw_dot_bacnet_dot_scan__pb2.RestartJobsReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ImportJob(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/normalgw.bacnet.Scan/ImportJob',
            normalgw_dot_bacnet_dot_scan__pb2.ImportJobRequest.SerializeToString,
            normalgw_dot_bacnet_dot_scan__pb2.ImportJobReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ObserveJobUpdates(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/normalgw.bacnet.Scan/ObserveJobUpdates',
            normalgw_dot_bacnet_dot_scan__pb2.ObserveJobUpdatesRequest.SerializeToString,
            normalgw_dot_bacnet_dot_scan__pb2.ObserveJobUpdatesReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetScanDeltas(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/normalgw.bacnet.Scan/GetScanDeltas',
            normalgw_dot_bacnet_dot_scan__pb2.GetScanDeltaRequest.SerializeToString,
            normalgw_dot_bacnet_dot_scan__pb2.GetScanDeltaReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)