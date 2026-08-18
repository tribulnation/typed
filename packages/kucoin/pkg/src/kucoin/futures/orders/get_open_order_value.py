"""`GET /api/v1/openOrderStatistics` — Get Open Order Value."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class FuturesOpenOrderValue(TypedDict):
  """Aggregate counts and values of active buy/sell orders for one contract."""

  openOrderBuySize: int
  """Total number of active buy orders."""
  openOrderSellSize: int
  """Total number of active sell orders."""
  openOrderBuyCost: str
  """Total value of active buy orders."""
  openOrderSellCost: str
  """Total value of active sell orders."""
  settleCurrency: str
  """Settlement currency."""


_Type = FuturesOpenOrderValue
adapter = validator[_Type](_Type)  # type: ignore


class GetOpenOrderValue(RpcEndpoint):
  """`Get Open Order Value` — mixed into `Orders`, the product exposing `futures.orders.get_open_order_value`."""

  async def get_open_order_value(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> FuturesOpenOrderValue:
    """Get the total count and value of this account's currently active (open) buy and sell orders for one contract.

    Args:
      symbol: Contract symbol.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
    }
    return await self.authed_request(
      'GET',
      '/api/v1/openOrderStatistics',
      params=params,
      validator=adapter,
      validate=validate,
    )
