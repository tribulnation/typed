from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class UsdMWsSessionResult(TypedDict):
  """Current WebSocket connection authentication state."""

  apiKey: str | None
  """The API key authenticating this connection, or null when unauthenticated."""
  authorizedSince: int | None
  """Time this connection was authenticated, milliseconds since epoch, or null when unauthenticated."""
  connectedSince: int
  """Time this WebSocket connection was established, milliseconds since epoch."""
  returnRateLimits: bool
  """Whether rate limit usage is included in every response on this connection."""
  serverTime: int
  """Current server time, milliseconds since epoch."""


class SessionStatus(WsRpcEndpoint):
  """Query this WebSocket connection's current authentication state."""

  async def session_status(
    self, *, validate: bool | None = None
  ) -> UsdMWsSessionResult:
    """Query this WebSocket connection's current authentication state.

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-api-general-info)
    """
    _Response = UsdMWsSessionResult
    _validator = validator[_Response](_Response)
    return await self.request('session.status', validator=_validator, validate=validate)
