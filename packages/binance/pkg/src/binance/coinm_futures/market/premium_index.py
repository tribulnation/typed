from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMMarkPriceInfo(TypedDict):
  """Index price, mark price, and latest funding rate for one symbol."""

  symbol: str
  """Trading symbol."""
  pair: str
  """Underlying pair."""
  markPrice: str
  """Mark price."""
  indexPrice: str
  """Index price."""
  estimatedSettlePrice: str
  """Estimated settlement price. Only meaningful in the last hour before settlement, but populated well before that too."""
  lastFundingRate: str
  """Latest funding rate. Perpetual symbols only -- "0.00000000" (not necessarily empty) on delivery symbols."""
  interestRate: str
  """Base asset interest rate. Perpetual symbols only -- "0.00000000" (not necessarily empty) on delivery symbols."""
  nextFundingTime: int
  """Next funding time, in milliseconds since epoch. Perpetual symbols only -- 0 on delivery symbols."""
  time: int
  """Current time, in milliseconds since epoch."""


class PremiumIndex(RpcEndpoint):
  """Index price and mark price, for a symbol, for every symbol of a pair, or for every symbol."""

  async def premium_index(
    self,
    *,
    symbol: str | None = None,
    pair: str | None = None,
    validate: bool | None = None,
  ) -> list[CoinMMarkPriceInfo]:
    """Index price and mark price, for a symbol, for every symbol of a pair, or for every symbol.

    Args:
      symbol: Symbol. Mutually exclusive with `pair`. Omit to get every symbol.
      pair: Underlying pair. Mutually exclusive with `symbol`. Returns every symbol of the pair.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#index-price-and-mark-price)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if pair is not None:
      params['pair'] = pair
    _Response = list[CoinMMarkPriceInfo]
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/dapi/v1/premiumIndex',
      params=params,
      validator=_validator,
      validate=validate,
    )
