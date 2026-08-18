from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class SessionStatus(TypedDict):
  """Authentication status of the WebSocket connection."""

  apiKey: str | None
  """The API key authenticated on this connection, or null if the connection is not authenticated."""
  authorizedSince: Timestamp | None
  """Millisecond timestamp this connection was authenticated, or null if the connection is not authenticated."""
  connectedSince: Timestamp
  """Millisecond timestamp this WebSocket connection was established."""
  returnRateLimits: bool
  """Whether rate limit usage is included in responses on this connection."""
  serverTime: Timestamp
  """Current server time."""
  userDataStream: bool
  """Whether a User Data Stream subscription is active on this connection."""


class SessionStatusEndpoint(WsRpcEndpoint):
  """Query session status"""

  async def session_status(self, *, validate: bool | None = None) -> SessionStatus:
    """Query the status of the WebSocket connection, inspecting which API key (if any) is used to authorize requests.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-api.md#session-status)
    """
    _Response = SessionStatus
    _validator = validator[_Response](_Response)
    return await self.request('session.status', validator=_validator, validate=validate)
