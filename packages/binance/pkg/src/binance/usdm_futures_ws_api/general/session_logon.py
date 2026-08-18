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


class SessionLogon(WsRpcEndpoint):
  """Authenticate this WebSocket connection with an API key, so that later requests on it can omit apiKey/signature. Binance restricts this method to Ed25519 keys."""

  async def session_logon(
    self,
    *,
    api_key: str,
    signature: str,
    validate: bool | None = None,
  ) -> UsdMWsSessionResult:
    """Authenticate this WebSocket connection with an API key, so that later requests on it can omit apiKey/signature. Binance restricts this method to Ed25519 keys.

    Args:
      api_key: API key to authenticate this connection with.
      signature: Ed25519 signature over the signed parameter string.

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-api-general-info)
    """
    params: dict = {
      'apiKey': api_key,
      'signature': signature,
    }
    _Response = UsdMWsSessionResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'session.logon', params=params, validator=_validator, validate=validate
    )
