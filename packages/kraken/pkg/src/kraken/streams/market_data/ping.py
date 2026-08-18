"""`streams.market_data.ping` -- WebSocket trading method."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.ws_rpc import WsRpcEndpoint


class PongReply(TypedDict):
  """The reply to a `ping` request."""

  method: Literal['pong']
  """Always `pong` -- note this differs from the request's own `method` value of `ping`."""
  req_id: NotRequired[int]
  """Client-originated request identifier, echoed back if one was sent."""
  success: NotRequired[bool]
  """Indicates if the request was successfully processed by the engine."""
  error: NotRequired[str]
  """Error message, present when `success` is `false`."""
  time_in: str
  """RFC3339 timestamp when the request was received on the wire, just prior to parsing."""
  time_out: str
  """RFC3339 timestamp when the response was sent on the wire, just prior to transmitting."""


validate_ping = validator(PongReply)


class Ping(WsRpcEndpoint):
  """`streams.market_data.ping`."""

  async def ping(self) -> PongReply:
    """Application-level ping to verify the WebSocket connection is alive -- distinct from the WebSocket protocol's own ping frames. The server answers with a `pong`. Useful to keep an otherwise-idle connection open (Kraken closes any connection after roughly a minute of inactivity).

    References:
      - [Official docs](https://docs.kraken.com/exchange/api-reference/spot-websocket-v2/ping)
    """
    return await self.raw_request('ping', validator=validate_ping)
