"""dYdX indexer list orders types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from .. import timestamp as ts
from typing_extensions import Literal, NotRequired, TypedDict
from .core import IndexerMixin, response_parser

class Order(TypedDict):
  """Order payload."""
  id: str
  subaccountId: str
  clientId: str
  clobPairId: str
  side: Literal['BUY', 'SELL']
  size: Decimal
  totalFilled: Decimal
  price: Decimal
  type: Literal['LIMIT', 'MARKET', 'STOP_LIMIT', 'STOP_MARKET', 'TRAILING_STOP', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET', 'HARD_TRADE', 'FAILED_HARD_TRADE', 'TRANSFER_PLACEHOLDER']
  status: Literal['OPEN', 'FILLED', 'CANCELED', 'BEST_EFFORT_CANCELED', 'UNTRIGGERED', 'BEST_EFFORT_OPENED', 'PENDING']
  timeInForce: Literal['GTT', 'IOC', 'FOK']
  reduceOnly: NotRequired[bool | None]
  orderFlags: str
  goodTilBlock: NotRequired[str | None]
  goodTilBlockTime: NotRequired[datetime | None]
  createdAtHeight: NotRequired[str | None]
  clientMetadata: NotRequired[str | None]
  triggerPrice: NotRequired[Decimal | None]
  postOnly: NotRequired[bool | None]
  ticker: str
  updatedAt: NotRequired[datetime | None]
  updatedAtHeight: NotRequired[str | None]
  subaccountNumber: int
  orderRouterAddress: NotRequired[str|None]
  builderFee: NotRequired[Decimal | None]
  feePpm: NotRequired[Decimal | None]

parse_response = response_parser(list[Order])

@dataclass
class ListOrders(IndexerMixin):
  """Endpoint mixin for ListOrders."""
  async def list_orders(
    self,
    address: str,
    *,
    subaccount: int,
    limit: int | None = None,
    ticker: str | None = None,
    side: Literal['BUY', 'SELL'] | None = None,
    status: Literal[
      'OPEN', 'FILLED', 'CANCELED', 'BEST_EFFORT_CANCELED', 'UNTRIGGERED', 'BEST_EFFORT_OPENED', 'PENDING'
    ] | None = None,
    type: Literal[
      'LIMIT', 'MARKET', 'STOP_LIMIT', 'STOP_MARKET', 'TRAILING_STOP', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET', 'HARD_TRADE', 'FAILED_HARD_TRADE', 'TRANSFER_PLACEHOLDER'
    ] | None = None,
    good_til_block_before_or_at: int | None = None,
    good_til_block_time_before_or_at: datetime | None = None,
    return_latest_orders: bool | None = None,
    validate: bool | None = None
  ) -> list[Order]:
    """List orders.
  
    Args:
      address: Wallet address that owns the subaccount.
      subaccount: Subaccount number.
      limit: Maximum number of orders to return.
      ticker: Ticker filter.
      side: Order side filter.
      status: Order status filter.
      type: Order type filter.
      good_til_block_before_or_at: Latest good-til-block to include.
      good_til_block_time_before_or_at: Latest good-til-block time to include.
      return_latest_orders: Whether to return only the latest orders.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http#list-orders)
    """
    params: dict[str, object] = {
      'address': address,
      'subaccountNumber': subaccount,
    }
    if limit is not None:
      params['limit'] = limit
    if ticker is not None:
      params['ticker'] = ticker
    if side is not None:
      params['side'] = side
    if status is not None:
      params['status'] = status
    if type is not None:
      params['type'] = type
    if good_til_block_before_or_at is not None:
      params['goodTilBlockBeforeOrAt'] = good_til_block_before_or_at
    if good_til_block_time_before_or_at is not None:
      params['goodTilBlockTimeBeforeOrAt'] = ts.dump(good_til_block_time_before_or_at)
    if return_latest_orders is not None:
      params['returnLatestOrders'] = return_latest_orders
    r = await self.request('GET', '/v4/orders', params=params)
    return parse_response(r, validate=self.validate(validate))
