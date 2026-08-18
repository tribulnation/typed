"""`streams.trading.amend_order` -- WebSocket trading method."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.ws_rpc import WsRpcEndpoint


class AmendOrderResult(TypedDict):
  """Result of a successful `amend_order` call."""

  amend_id: NotRequired[str]
  """Unique Kraken identifier generated for this amend transaction."""
  order_id: NotRequired[str]
  """Kraken order identifier, if populated in the request."""
  cl_ord_id: NotRequired[str]
  """Client identifier, if populated in the request."""
  warnings: NotRequired[list[str]]
  """Non-fatal warnings about the amend, if any."""


validate_amend_order = validator(AmendOrderResult)


class AmendOrder(WsRpcEndpoint):
  """`streams.trading.amend_order`."""

  async def amend_order(
    self,
    *,
    order_id: str | None = None,
    cl_ord_id: str | None = None,
    order_qty: float | None = None,
    display_qty: float | None = None,
    limit_price: float | None = None,
    limit_price_type: Literal['static', 'pct', 'quote'] | None = None,
    post_only: bool | None = None,
    trigger_price: float | None = None,
    trigger_price_type: Literal['static', 'pct', 'quote'] | None = None,
    deadline: str | None = None,
    symbol: str | None = None,
  ) -> AmendOrderResult:
    """Modifies the parameters of a live order in-place, without cancelling and re-creating it: order identifiers stay the same, queue priority in the order book is maintained where possible, and if the amendment reduces the order quantity below the already-filled quantity, the remaining quantity is cancelled. Supersedes the legacy `edit_order` (cancel-replace), which loses queue priority and has several unsupported-order-shape caveats.

    Args:
      order_id: Kraken identifier for the order to amend, e.g. `OFGKYQ-FHPCQ-HUQFEK`. Either `order_id` or `cl_ord_id` is required.
      cl_ord_id: Client identifier for the order to amend, e.g. `6d1b345e-2821-40e2-ad83-4ecb18a06876`. Either `order_id` or `cl_ord_id` is required.
      order_qty: New order quantity in terms of the base asset.
      display_qty: For iceberg orders only: new quantity to show in the book while the rest of the remaining order quantity stays hidden. Minimum value is 1/15 of the remaining order quantity.
      limit_price: New limit price restriction, used with `limit_price_type`. For order types that support a limit price only.
      limit_price_type: Units for `limit_price`: `static` (a static market price), `pct` (a percentage offset from the reference price), or `quote` (a notional offset in the quote currency). `static` is the default for all order types except `trailing-stop-limit`, which defaults to `quote`. Currently only available on trailing-stop-limit orders.
      post_only: Optional for limit-price amends. If `true`, rejects the limit-price change if the order cannot be posted passively in the book.
      trigger_price: New trigger price to activate the order, used with `trigger_price_type`. For triggered order types only.
      trigger_price_type: Units for `trigger_price`. For triggered order types only.
      deadline: RFC3339 timestamp, millisecond precision. Valid offsets from the current time range from 500ms to 60s (default 5s). The engine will not match this order after this time.
      symbol: Required on amends for non-crypto pairs, i.e. provide the pair symbol for xstocks, e.g. `TSLAx/USD`.

    References:
      - [Official docs](https://docs.kraken.com/exchange/api-reference/spot-websocket-v2/amend_order)
    """
    params = {}
    if order_id is not None:
      params['order_id'] = order_id
    if cl_ord_id is not None:
      params['cl_ord_id'] = cl_ord_id
    if order_qty is not None:
      params['order_qty'] = order_qty
    if display_qty is not None:
      params['display_qty'] = display_qty
    if limit_price is not None:
      params['limit_price'] = limit_price
    if limit_price_type is not None:
      params['limit_price_type'] = limit_price_type
    if post_only is not None:
      params['post_only'] = post_only
    if trigger_price is not None:
      params['trigger_price'] = trigger_price
    if trigger_price_type is not None:
      params['trigger_price_type'] = trigger_price_type
    if deadline is not None:
      params['deadline'] = deadline
    if symbol is not None:
      params['symbol'] = symbol

    return await self.request('amend_order', params, validator=validate_amend_order)
