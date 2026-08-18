"""`spot.trading.get_websockets_token` -- private Spot endpoint."""

from typing_extensions import NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class WebSocketsToken(TypedDict):
  """A short-lived token authenticating a private WebSocket connection."""

  token: NotRequired[str]
  """WebSocket authentication token."""
  expires: NotRequired[int]
  """Seconds after which the token expires (~900), unless already consumed by a private WebSocket subscription."""


validate_get_websockets_token = validator(WebSocketsToken)


class GetWebsocketsToken(RpcEndpoint):
  """`spot.trading.get_websockets_token`."""

  async def get_websockets_token(self) -> WebSocketsToken:
    """Request an authentication token for connecting to and authenticating with Kraken's private WebSocket API. The token should be used within 15 minutes of issuance; once a successful connection and private subscription has been made, it does not expire for the life of that connection.

    **API Key Permissions Required:** `WebSocket interface - On`

    References:
      - [Official docs](https://docs.kraken.com/api-reference/trading/get-websockets-token)
    """
    return await self.authed_request(
      '/0/private/GetWebSocketsToken', validator=validate_get_websockets_token
    )
