"""WebSocket base classes for various kinds of communication protocols.

- `Socket`: minimal client, handling connection, pinging, and listening.
- `Rpc`: multiplexed request/response client, via message IDs.
- `Streams`: multiplex subscribe/stream client (supports multiple concurrent subscriptions).
- `StreamsRpc`: multiplexed request/response and streams socket client, via message and channel IDs.
- `SerialReplies`: mixin for a connection whose replies carry no correlation id — compose
  with `Streams`/`Rpc`/`StreamsRpc`, not instead of one; a venue can mix correlation
  strategies (id-correlated RPC, arrival-order-correlated subscribe/unsubscribe, or the
  reverse) freely.
"""
from .socket import Socket
from .rpc import Rpc
from .streams import Streams
from .streams_rpc import StreamsRpc
from .serial import SerialReplies

__all__ = [
  'Socket',
  'Rpc',
  'Streams',
  'StreamsRpc',
  'SerialReplies',
]
