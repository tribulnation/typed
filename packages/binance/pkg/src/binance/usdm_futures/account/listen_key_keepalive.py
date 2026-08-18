from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class UsdMFuturesListenKey(TypedDict):
  """Listen key identifying a user data stream."""

  listenKey: NotRequired[str]
  """Listen key used to connect to the user data WebSocket stream."""


class ListenKeyKeepalive(RpcEndpoint):
  """Keepalive User Data Stream"""

  async def listen_key_keepalive(
    self,
    *,
    validate: bool | None = None,
  ) -> UsdMFuturesListenKey:
    """Keepalive a user data stream to prevent a time out. User data streams will close after 60 minutes. It's recommended to send a ping about every 60 minutes.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/user-data-streams#keepalive-user-data-stream)
    """
    _Response = UsdMFuturesListenKey
    _validator = validator[_Response](_Response)
    return await self.request(
      'PUT', '/fapi/v1/listenKey', validator=_validator, validate=validate
    )
