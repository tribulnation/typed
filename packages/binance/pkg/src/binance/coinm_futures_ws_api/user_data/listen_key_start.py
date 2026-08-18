from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class CoinMWsListenKey(TypedDict):
  """Listen key identifying a user data stream."""

  listenKey: NotRequired[str]
  """Listen key used to connect to the user data WebSocket stream."""


class ListenKeyStart(WsRpcEndpoint):
  """Start a new user data stream. The stream will close after 60 minutes unless a keepalive is sent. If the account has an active `listenKey`, that `listenKey` will be returned and its validity will be extended for 60 minutes."""

  async def listen_key_start(self, *, validate: bool | None = None) -> CoinMWsListenKey:
    """Start a new user data stream. The stream will close after 60 minutes unless a keepalive is sent. If the account has an active `listenKey`, that `listenKey` will be returned and its validity will be extended for 60 minutes.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/ws-api/user-data-streams#start-user-data-stream)
    """
    _Response = CoinMWsListenKey
    _validator = validator[_Response](_Response)
    return await self.request(
      'userDataStream.start', validator=_validator, validate=validate
    )
