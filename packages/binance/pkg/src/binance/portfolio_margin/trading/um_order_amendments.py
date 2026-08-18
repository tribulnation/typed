from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmUmModifyOrderHistory(TypedDict):
  """PmUmModifyOrderHistory."""

  amendmentId: NotRequired[int]
  """Order modification ID."""
  symbol: NotRequired[str]
  """Trade symbol, if existing."""
  pair: NotRequired[str]
  """Pair."""
  orderId: NotRequired[int]
  """Normal orderID after trigger if appliable, only have when the strategy is triggered."""
  clientOrderId: NotRequired[str]
  """Client Order ID."""
  time: NotRequired[Timestamp]
  """Order modification time."""
  priceMatch: NotRequired[
    Literal[
      'OPPONENT',
      'OPPONENT_5',
      'OPPONENT_10',
      'OPPONENT_20',
      'QUEUE',
      'QUEUE_5',
      'QUEUE_10',
      'QUEUE_20',
    ]
  ]
  """Price Match."""


class UmOrderAmendments(RpcEndpoint):
  """Query UM Modify Order History"""

  async def um_order_amendments(
    self,
    *,
    symbol: str,
    order_id: int | None = None,
    orig_client_order_id: str | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[PmUmModifyOrderHistory]:
    """Get order modification history.

    Args:
      symbol: Symbol.
      order_id: Order ID.
      orig_client_order_id: Client order ID.
      start_time: Timestamp in ms to get funding from INCLUSIVE.
      end_time: Timestamp in ms to get funding until INCLUSIVE.
      limit: Number of results returned.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#query-um-modify-order-history)
    """
    params: dict = {
      'symbol': symbol,
    }
    if order_id is not None:
      params['orderId'] = order_id
    if orig_client_order_id is not None:
      params['origClientOrderId'] = orig_client_order_id
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if limit is not None:
      params['limit'] = limit
    _Response = list[PmUmModifyOrderHistory]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/um/orderAmendment',
      params=params,
      validator=_validator,
      validate=validate,
    )
