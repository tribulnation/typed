"""`GET /api/v2/getMaxOpenSize` — Get Max Open Size."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class MaxOpenSize(TypedDict):
  """Maximum position size a symbol could be opened to at a given price/leverage."""

  symbol: str
  """Symbol of the contract."""
  maxBuyOpenSize: int
  """Maximum buy (long) open size, in lots."""
  maxSellOpenSize: int
  """Maximum sell (short) open size, in lots."""


_Type = MaxOpenSize
adapter = validator[_Type](_Type)  # type: ignore


class GetMaxOpenSize(RpcEndpoint):
  """`Get Max Open Size` — mixed into `Positions`, the product exposing `futures.positions.get_max_open_size`."""

  async def get_max_open_size(
    self,
    *,
    symbol: str,
    price: str,
    leverage: int,
    validate: bool | None = None,
  ) -> MaxOpenSize:
    """Get the maximum position size (in lots) that could be opened on a symbol at a given price and leverage, for both the buy (long) and sell (short) direction.

    Args:
      symbol: Symbol of the contract, e.g. `XBTUSDTM`.
      price: Order price to size against.
      leverage: Leverage to size against.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
      'price': price,
      'leverage': leverage,
    }
    return await self.authed_request(
      'GET',
      '/api/v2/getMaxOpenSize',
      params=params,
      validator=adapter,
      validate=validate,
    )
