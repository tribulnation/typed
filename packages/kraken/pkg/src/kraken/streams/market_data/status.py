"""`streams.market_data.status` -- WebSocket channel subscription."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from typed_core.util import StreamManager
from ...core.endpoint.stream import StreamEndpoint


class StatusData(TypedDict):
  """Exchange status data."""

  system: Literal['online', 'cancel_only', 'maintenance', 'post_only', 'limit_only']
  """The status of the trading engine. `online`: markets operate normally. `maintenance`: markets are offline, no orders can be placed or cancelled. `cancel_only`: orders can be cancelled but not placed, no matching occurs. `post_only`: only `post_only` limit orders can be submitted, orders can be cancelled, no matching occurs. `limit_only`: documented separately on the WebSocket reconnection guide, not on this channel's own reference page."""
  api_version: Literal['v2']
  """The version of the WebSocket API."""
  connection_id: int
  """A unique connection identifier, for debugging."""
  version: str
  """The version of the WebSocket service."""


class StatusMessage(TypedDict):
  """A `status` channel push."""

  channel: Literal['status']
  """The channel this push belongs to."""
  type: Literal['update']
  """This channel only ever pushes `update` -- there is no `snapshot` type."""
  data: list[StatusData]
  """One entry describing the current exchange status."""


validate_status = validator(StatusMessage)


class Status(StreamEndpoint):
  """`streams.market_data.status`."""

  def status(self) -> StreamManager[StatusMessage, object, object]:
    """Subscribe to exchange status: automatically pushed once on successful connection and again whenever the trading engine status changes. There is no way to directly request a fresh status update.

    References:
      - [Official docs](https://docs.kraken.com/exchange/api-reference/spot-websocket-v2/status)
    """
    return self.subscribe('status', validator=validate_status)
