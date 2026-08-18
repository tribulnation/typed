from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class MarginCancelOcoOrderReport(TypedDict):
  """One order-list leg's cancellation acknowledgement."""

  symbol: str
  """Trading pair symbol."""
  origClientOrderId: str
  """Client order id of the leg as it was before this cancellation."""
  orderId: int
  """Order id."""
  orderListId: int
  """Id of the order list this order belongs to."""
  clientOrderId: str
  """Client id assigned to this cancellation request."""
  price: str
  """Order price."""
  origQty: str
  """Original order quantity."""
  executedQty: str
  """Cumulative filled quantity."""
  cummulativeQuoteQty: str
  """Cumulative quote asset transacted quantity."""
  status: Literal[
    'NEW',
    'PENDING_NEW',
    'PARTIALLY_FILLED',
    'FILLED',
    'CANCELED',
    'PENDING_CANCEL',
    'REJECTED',
    'EXPIRED',
    'EXPIRED_IN_MATCH',
  ]
  """Order status."""
  timeInForce: Literal['GTC', 'IOC', 'FOK']
  """Time in force."""
  type: Literal[
    'LIMIT',
    'MARKET',
    'STOP_LOSS',
    'STOP_LOSS_LIMIT',
    'TAKE_PROFIT',
    'TAKE_PROFIT_LIMIT',
    'LIMIT_MAKER',
  ]
  """Order type."""
  side: Literal['BUY', 'SELL']
  """Order side."""
  stopPrice: str
  """Price at which the leg's stop triggers. "0.000000" for the non-stop leg."""


class MarginCancelOpenOrderResult(TypedDict):
  """Result of canceling one plain (non-order-list) margin order as part of canceling all open orders on a symbol."""

  symbol: str
  """Trading pair symbol."""
  isIsolated: bool
  """Whether the order belongs to an isolated margin account."""
  origClientOrderId: str
  """Client order id of the order as it was before this cancellation."""
  orderId: int
  """Order id."""
  orderListId: int
  """Id of the order list this order belongs to, or -1 if it is not part of one."""
  clientOrderId: str
  """Client id assigned to this cancellation request."""
  price: str
  """Order price."""
  origQty: str
  """Original order quantity."""
  executedQty: str
  """Cumulative filled quantity."""
  cummulativeQuoteQty: str
  """Cumulative quote asset transacted quantity."""
  status: Literal[
    'NEW',
    'PENDING_NEW',
    'PARTIALLY_FILLED',
    'FILLED',
    'CANCELED',
    'PENDING_CANCEL',
    'REJECTED',
    'EXPIRED',
    'EXPIRED_IN_MATCH',
  ]
  """Order status."""
  timeInForce: Literal['GTC', 'IOC', 'FOK']
  """Time in force."""
  type: Literal[
    'LIMIT',
    'MARKET',
    'STOP_LOSS',
    'STOP_LOSS_LIMIT',
    'TAKE_PROFIT',
    'TAKE_PROFIT_LIMIT',
    'LIMIT_MAKER',
  ]
  """Order type."""
  side: Literal['BUY', 'SELL']
  """Order side."""


class MarginOrderListOrder(TypedDict):
  """One order belonging to the order list, identified minimally."""

  symbol: str
  """Trading pair symbol."""
  orderId: int
  """Order id."""
  clientOrderId: str
  """Client order id, either caller-supplied or venue-generated."""


class MarginCancelOcoOrderResult(TypedDict):
  """Result of canceling an entire margin OCO order list."""

  orderListId: int
  """Id of the canceled order list."""
  contingencyType: Literal['OCO']
  """Contingency type of the order list."""
  listStatusType: Literal['RESPONSE', 'EXEC_STARTED', 'UPDATED', 'ALL_DONE']
  """Status of the order list."""
  listOrderStatus: Literal['EXECUTING', 'ALL_DONE', 'REJECT']
  """Execution status of the order list."""
  listClientOrderId: str
  """Client id for the entire order list, either caller-supplied or venue-generated."""
  transactionTime: Timestamp
  """Time the cancellation was processed."""
  symbol: str
  """Trading pair symbol."""
  isIsolated: bool
  """Whether the order list belongs to an isolated margin account."""
  orders: list[MarginOrderListOrder]
  """The legs that made up the canceled OCO, identified minimally."""
  orderReports: list[MarginCancelOcoOrderReport]
  """Per-leg cancellation acknowledgements."""


class CancelOpenOrders(RpcEndpoint):
  """Cancel all active orders on a symbol for a margin account, including any OCO order lists on that symbol."""

  async def cancel_open_orders(
    self,
    *,
    symbol: str,
    is_isolated: Literal['TRUE', 'FALSE'] | None = None,
    validate: bool | None = None,
  ) -> list[MarginCancelOpenOrderResult | MarginCancelOcoOrderResult]:
    """Cancel all active orders on a symbol for a margin account, including any OCO order lists on that symbol.

    Args:
      symbol: Trading pair symbol, e.g. BNBUSDT.
      is_isolated: Margin account type for this order: isolated when TRUE, crossed (default) when FALSE.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/trade#margin-account-cancel-all-open-orders-on-asymbol)
    """
    params: dict = {
      'symbol': symbol,
    }
    if is_isolated is not None:
      params['isIsolated'] = is_isolated
    _Response = list[MarginCancelOpenOrderResult | MarginCancelOcoOrderResult]
    _validator = validator[_Response](_Response)  # type: ignore
    return await self.authed_request(
      'DELETE',
      '/sapi/v1/margin/openOrders',
      params=params,
      validator=_validator,
      validate=validate,
    )
