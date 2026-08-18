from typing_extensions import Any
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SpecialKeyDelete(RpcEndpoint):
  """Delete a special (low-latency trading) API key. Omit `symbol` to delete the cross margin special key, or set it to delete an isolated margin symbol's special key."""

  async def special_key_delete(
    self,
    *,
    api_name: str | None = None,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> dict[str, Any]:
    """Delete a special (low-latency trading) API key. Omit `symbol` to delete the cross margin special key, or set it to delete an isolated margin symbol's special key.

    Args:
      api_name: Name of the special key to delete.
      symbol: Isolated margin trading pair, e.g. BTCUSDT. Omit to delete the cross margin special key; set to delete an isolated margin symbol's special key instead.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#delete-special-key)
    """
    params = {}
    if api_name is not None:
      params['apiName'] = api_name
    if symbol is not None:
      params['symbol'] = symbol
    _Response = dict[str, Any]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'DELETE',
      '/sapi/v1/margin/apiKey',
      params=params,
      validator=_validator,
      validate=validate,
    )
