from typing_extensions import AsyncIterator, Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MarginForceLiquidationOrder(TypedDict):
  """A single order placed by the forced liquidation engine."""

  avgPrice: str
  """Average fill price, as a decimal string."""
  executedQty: str
  """Quantity filled, as a decimal string."""
  orderId: int
  """Order ID."""
  price: str
  """Order price, as a decimal string."""
  qty: str
  """Order quantity, as a decimal string."""
  side: Literal['BUY', 'SELL']
  """Order side."""
  symbol: str
  """Symbol the order was placed on."""
  timeInForce: Literal['GTC', 'IOC', 'FOK']
  """Time in force."""
  isIsolated: bool
  """Whether this liquidation was on an isolated margin account."""
  updatedTime: int
  """Millisecond timestamp this order was last updated."""


class MarginForceLiquidationRecords(TypedDict):
  """Page of forced liquidation orders."""

  rows: list[MarginForceLiquidationOrder]
  """Matching forced liquidation orders on this page."""
  total: int
  """Total number of matching records across all pages."""


class ForceLiquidationRecord(RpcEndpoint):
  """Get Force Liquidation Record"""

  async def force_liquidation_record(
    self,
    *,
    start_time: int | None = None,
    end_time: int | None = None,
    isolated_symbol: str | None = None,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> MarginForceLiquidationRecords:
    """Query this margin account's forced liquidation orders. Response is in descending order.

    Args:
      start_time: Query period start, as milliseconds since epoch.
      end_time: Query period end, as milliseconds since epoch.
      isolated_symbol: Isolated symbol to query. Returns cross-margin liquidations when omitted.
      current: Page to fetch, 1-indexed.
      size: Number of records per page. Max 100.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#get-force-liquidation-record)
    """
    params = {}
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if isolated_symbol is not None:
      params['isolatedSymbol'] = isolated_symbol
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    _Response = MarginForceLiquidationRecords
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/margin/forceLiquidationRec',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def force_liquidation_record_paged(
    self,
    *,
    start_time: int | None = None,
    end_time: int | None = None,
    isolated_symbol: str | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[MarginForceLiquidationRecords]:
    """Yield successive pages of `force_liquidation_record`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.force_liquidation_record(
        start_time=start_time,
        end_time=end_time,
        isolated_symbol=isolated_symbol,
        size=size,
        current=current,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or size is None or pages * size >= total:
        break
      current += 1
