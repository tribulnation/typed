from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class CoinMWsSessionResult(TypedDict):
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


class SessionLogout(WsRpcEndpoint):
  """Forget the API key associated with this connection. The connection stays open; later requests must again supply apiKey/signature explicitly."""

  async def session_logout(
    self, *, validate: bool | None = None
  ) -> CoinMWsSessionResult:
    """Forget the API key associated with this connection. The connection stays open; later requests must again supply apiKey/signature explicitly.

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/coin-margined-futures/websocket-api-general-info)
    """
    _Response = CoinMWsSessionResult
    _validator = validator[_Response](_Response)
    return await self.request('session.logout', validator=_validator, validate=validate)
