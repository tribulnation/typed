from typing_extensions import Any
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class LegacyIsolatedListenKeyClose(RpcEndpoint):
  """Close an isolated margin user data stream (legacy path)."""

  async def legacy_isolated_listen_key_close(
    self,
    *,
    symbol: str,
    listen_key: str,
    validate: bool | None = None,
  ) -> dict[str, Any]:
    """Close an isolated margin user data stream (legacy path).

    Args:
      symbol: Isolated margin trading pair symbol whose user data stream to close, e.g. `BTCUSDT`.
      listen_key: Listen key returned by `legacy_isolated_listen_key_create`, identifying the isolated margin stream to close.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/margin-api.md)
    """
    params: dict = {
      'symbol': symbol,
      'listenKey': listen_key,
    }
    _Response = dict[str, Any]
    _validator = validator[_Response](_Response)
    return await self.request(
      'DELETE',
      '/sapi/v1/userDataStream/isolated',
      params=params,
      validator=_validator,
      validate=validate,
    )
