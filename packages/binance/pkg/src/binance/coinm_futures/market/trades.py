from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMTrade(TypedDict):
  """One market trade."""

  id: int
  """Trade ID."""
  price: str
  """Trade price."""
  qty: str
  """Trade quantity, in contracts."""
  baseQty: str
  """Trade quantity, in base asset."""
  time: int
  """Trade time, in milliseconds since epoch."""
  isBuyerMaker: bool
  """Whether the buyer was the maker."""


class Trades(RpcEndpoint):
  """Recent market trades for a symbol. Only filled market trades are returned -- insurance-fund and ADL trades are excluded."""

  async def trades(
    self,
    *,
    symbol: str,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[CoinMTrade]:
    """Recent market trades for a symbol. Only filled market trades are returned -- insurance-fund and ADL trades are excluded.

    Args:
      symbol: Symbol.
      limit: Number of trades to return.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#recent-trades-list)
    """
    params: dict = {
      'symbol': symbol,
    }
    if limit is not None:
      params['limit'] = limit
    _Response = list[CoinMTrade]
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET', '/dapi/v1/trades', params=params, validator=_validator, validate=validate
    )
