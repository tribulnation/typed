"""Pin the gRPC transport primitives promoted from typed-dydx's `chain/core.py` (design doc §9):
`wrap_exceptions` mapping a transport failure to `NetworkError`, and `GrpcClient.channel`'s
lazy-construction contract, mirroring `test_http.py`/`test_socket.py`'s own reasoning for the
other two transports.
"""
import pytest
from grpclib.exceptions import ProtocolError
from typed_core.exceptions import NetworkError
from typed_core.grpc import GrpcClient, GrpcEndpoint, wrap_exceptions

@wrap_exceptions
async def _raises_protocol_error():
  """Always raise a transport-level `ProtocolError`, for `wrap_exceptions` to normalize."""
  raise ProtocolError('boom')

@pytest.mark.asyncio
async def test_wrap_exceptions_maps_transport_failure_to_network_error():
  """A grpclib transport failure surfaces as `typed_core.exceptions.NetworkError`."""
  with pytest.raises(NetworkError):
    await _raises_protocol_error()

@pytest.mark.asyncio
async def test_grpc_client_channel_is_lazy():
  """`GrpcClient.channel` is built on first access, not at construction.

  Run under `pytest.mark.asyncio` (matching this package's other transport tests, e.g.
  `test_socket.py`/`test_http.py`) so a running event loop is present when `.channel`
  triggers grpclib's `Channel(...)` construction -- `grpclib.client.Channel.__init__`
  calls `asyncio.get_event_loop()` directly, which raises outside a running loop once a
  prior test's own loop has been torn down.
  """
  client = GrpcClient(host='example.com', port=443)
  assert 'channel' not in client.__dict__
  _ = client.channel
  assert 'channel' in client.__dict__
