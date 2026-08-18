from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class LegacyIsolatedMarginListenKey(TypedDict):
  """Listen key identifying an isolated margin user data stream (legacy path)."""

  listenKey: str
  """Listen key used to connect to the isolated margin user data WebSocket stream."""


class LegacyIsolatedListenKeyCreate(RpcEndpoint):
  """Start a new isolated margin user data stream (legacy path) for one symbol and return a listen key used to connect to it over WebSocket. The stream closes after 60 minutes unless kept alive; if the account already has an active listen key for this symbol, that key is returned and its validity extended."""

  async def legacy_isolated_listen_key_create(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> LegacyIsolatedMarginListenKey:
    """Start a new isolated margin user data stream (legacy path) for one symbol and return a listen key used to connect to it over WebSocket. The stream closes after 60 minutes unless kept alive; if the account already has an active listen key for this symbol, that key is returned and its validity extended.

    Args:
      symbol: Isolated margin trading pair symbol whose user data stream to start, e.g. `BTCUSDT`.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/margin-api.md)
    """
    params: dict = {
      'symbol': symbol,
    }
    _Response = LegacyIsolatedMarginListenKey
    _validator = validator[_Response](_Response)
    return await self.request(
      'POST',
      '/sapi/v1/userDataStream/isolated',
      params=params,
      validator=_validator,
      validate=validate,
    )
