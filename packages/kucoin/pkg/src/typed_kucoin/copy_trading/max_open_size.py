"""`GET /api/v1/copy-trade/futures/get-max-open-size` — Get Max Open Size."""

from typed_core.validation import TypedDict, validator
from typed_kucoin.core import RpcEndpoint


class MaxOpenSizeResult(TypedDict):
  """Maximum order size a copy-trading account could open at a given price and leverage."""

  symbol: str
  maxBuyOpenSize: str
  """Maximum buy (long) open size."""
  maxSellOpenSize: str
  """Maximum sell (short) open size."""


adapter = validator(MaxOpenSizeResult)


class MaxOpenSize(RpcEndpoint):
  """`Get Max Open Size` — mixed into `CopyTrading`, the product exposing
  `copy_trading.max_open_size`."""

  async def max_open_size(
    self,
    *,
    symbol: str,
    price: float,
    leverage: int,
    validate: bool | None = None,
  ) -> MaxOpenSizeResult:
    """Get the maximum futures position size a copy-trading account could open right now.

    Args:
      symbol: Contract symbol, for example `XBTUSDTM`.
      price: Order price to size against.
      leverage: Leverage to size against.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {'symbol': symbol, 'price': price, 'leverage': leverage}
    return await self.authed_request(
      'GET',
      '/api/v1/copy-trade/futures/get-max-open-size',
      params=params,
      validator=adapter,
      validate=validate,
    )
