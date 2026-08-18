from datetime import datetime
from typing_extensions import Any, NotRequired, TypedDict
from bit2me.types import (
  OffsetParam,
  OrderSide,
  OrderType,
  SortDirectionParam,
  TradeResponse,
)
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class ListTradingTradesResponse(TypedDict):
  total: NotRequired[float]
  """Total number of trades matching the query, across all pages"""
  data: NotRequired[list[TradeResponse]]
  """Page of trades matching the query"""


validate_response = validator(ListTradingTradesResponse)


class List(RpcEndpoint):
  async def list(
    self,
    *,
    ids: Any | None = None,
    symbol: str | None = None,
    side: OrderSide | None = None,
    order_type: OrderType | None = None,
    limit: float | None = None,
    offset: OffsetParam | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    sort: str | None = None,
    direction: SortDirectionParam | None = None,
    validate: bool | None = None,
  ) -> ListTradingTradesResponse:
    """Get all user trades paged with a maximum page size of 50.
    The result can be filtered by dates and side optionally.

    Args:
      ids: Comma separated trade identifiers
      symbol: Filter trades by market symbol.
      side: Filter trades by side.
      order_type: Filter trades by the order type that produced them.
      limit: The maximum number of trades to fetch
      offset: The number of records the result should skip, in pages of `limit` size.
      start_time: Only return trades executed at or after this date time.
      end_time: Only return trades executed at or before this date time.
      sort: The field to sort
      direction: Sort direction applied to the `sort` field.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-rest#tag/trading/GET/v1/trading/trade)
    """
    params = {}
    if ids is not None:
      params['ids'] = ids
    if symbol is not None:
      params['symbol'] = symbol
    if side is not None:
      params['side'] = side
    if order_type is not None:
      params['orderType'] = order_type
    if limit is not None:
      params['limit'] = limit
    if offset is not None:
      params['offset'] = offset
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if sort is not None:
      params['sort'] = sort
    if direction is not None:
      params['direction'] = direction
    return await self.authed_request(
      'GET',
      '/v1/trading/trade',
      params=params,
      validator=validate_response,
      validate=validate,
    )
