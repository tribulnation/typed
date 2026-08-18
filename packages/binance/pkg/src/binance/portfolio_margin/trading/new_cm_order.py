from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmNewCmOrder(TypedDict):
  """Place new CM order."""

  clientOrderId: NotRequired[str]
  """Client Order ID."""
  cumQty: NotRequired[str]
  """Cum Qty."""
  executedQty: NotRequired[str]
  """Executed Qty."""
  orderId: NotRequired[int]
  """Normal orderID after trigger if appliable, only have when the strategy is triggered."""
  origQty: NotRequired[str]
  """Orig Qty."""
  price: NotRequired[str]
  """Price."""
  reduceOnly: NotRequired[bool]
  """Reduce Only."""
  side: NotRequired[Literal['BUY', 'SELL']]
  """Side."""
  positionSide: NotRequired[Literal['BOTH', 'LONG', 'SHORT']]
  """BOTH means that it is the position of One-way Mode."""
  status: NotRequired[str]
  """Enum：completed，processing."""
  symbol: NotRequired[str]
  """Trade symbol, if existing."""
  pair: NotRequired[str]
  """Pair."""
  timeInForce: NotRequired[Literal['GTC', 'IOC', 'FOK', 'GTX']]
  """Time In Force."""
  type: NotRequired[Literal['LIMIT', 'MARKET']]
  """Normal order type after trigger if appliable."""
  updateTime: NotRequired[Timestamp]
  """last update time."""


class NewCmOrder(RpcEndpoint):
  """New CM Order"""

  async def new_cm_order(
    self,
    *,
    symbol: str,
    side: Literal['BUY', 'SELL'],
    type: Literal['LIMIT', 'MARKET'],
    position_side: Literal['BOTH', 'LONG', 'SHORT'] | None = None,
    time_in_force: Literal['GTC', 'IOC', 'FOK', 'GTX'] | None = None,
    quantity: float | None = None,
    reduce_only: Literal['true', 'false'] | None = None,
    price: float | None = None,
    price_match: Literal[
      'OPPONENT',
      'OPPONENT_5',
      'OPPONENT_10',
      'OPPONENT_20',
      'QUEUE',
      'QUEUE_5',
      'QUEUE_10',
      'QUEUE_20',
    ]
    | None = None,
    new_client_order_id: str | None = None,
    new_order_resp_type: Literal['ACK', 'RESULT'] | None = None,
    validate: bool | None = None,
  ) -> PmNewCmOrder:
    """Place new CM order.

    Args:
      symbol: Symbol.
      side: Order side.
      type: Order type.
      position_side: Default `BOTH` for One-way Mode ; `LONG` or `SHORT` for Hedge Mode. It must be sent in Hedge Mode.
      time_in_force: Time in force.
      quantity: Place amount.
      reduce_only: \"true" or "false". Cannot be sent in Hedge Mode.
      price: Order price.
      price_match: only avaliable for `LIMIT`/`STOP`/`TAKE_PROFIT` order; can be set to `OPPONENT`/ `OPPONENT_5`/ `OPPONENT_10`/ `OPPONENT_20`: /`QUEUE`/ `QUEUE_5`/ `QUEUE_10`/ `QUEUE_20`; Can't be passed together with `price`.
      new_client_order_id: A unique id among open orders. Automatically generated if not sent. Can only be string following the rule: `^[.A-Z:/a-z0-9_-]{1,32}$`.
      new_order_resp_type: \"ACK", "RESULT", default "ACK".

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/trade#new-cm-order)
    """
    params: dict = {
      'symbol': symbol,
      'side': side,
      'type': type,
    }
    if position_side is not None:
      params['positionSide'] = position_side
    if time_in_force is not None:
      params['timeInForce'] = time_in_force
    if quantity is not None:
      params['quantity'] = quantity
    if reduce_only is not None:
      params['reduceOnly'] = reduce_only
    if price is not None:
      params['price'] = price
    if price_match is not None:
      params['priceMatch'] = price_match
    if new_client_order_id is not None:
      params['newClientOrderId'] = new_client_order_id
    if new_order_resp_type is not None:
      params['newOrderRespType'] = new_order_resp_type
    _Response = PmNewCmOrder
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/papi/v1/cm/order',
      params=params,
      validator=_validator,
      validate=validate,
    )
