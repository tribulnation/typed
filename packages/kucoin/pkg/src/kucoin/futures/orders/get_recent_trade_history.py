"""`GET /api/v1/recentFills` — Get Recent Trade History."""

from typed_core.validation import validator
from kucoin.types import FuturesTrade
from kucoin.core import RpcEndpoint


_Type = list[FuturesTrade]
adapter = validator[_Type](_Type)  # type: ignore


class GetRecentTradeHistory(RpcEndpoint):
  """`Get Recent Trade History` — mixed into `Orders`, the product exposing `futures.orders.get_recent_trade_history`."""

  async def get_recent_trade_history(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> list[FuturesTrade]:
    """Get up to 1000 of this account's own fills from the last 24 hours -- a lower-latency alternative to Get Trade History for recent activity. Data is not guaranteed real-time.

    Args:
      symbol: Contract symbol to filter by.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    return await self.authed_request(
      'GET',
      '/api/v1/recentFills',
      params=params,
      validator=adapter,
      validate=validate,
    )
