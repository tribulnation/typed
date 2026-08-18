"""`spot.trading.amend_order` -- private Spot endpoint."""

from typing_extensions import NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class OrderAmended(TypedDict):
  """Result of amending a live order."""

  amend_id: NotRequired[str]
  """The unique Kraken identifier generated for this amend transaction."""


validate_amend_order = validator(OrderAmended)


class AmendOrder(RpcEndpoint):
  """`spot.trading.amend_order`."""

  async def amend_order(
    self,
    *,
    txid: str | None = None,
    cl_ord_id: str | None = None,
    order_qty: str | None = None,
    display_qty: str | None = None,
    limit_price: str | None = None,
    trigger_price: str | None = None,
    pair: str | None = None,
    post_only: bool | None = None,
    deadline: str | None = None,
  ) -> OrderAmended:
    """Modify an existing order's parameters in place, without cancelling and replacing it: Kraken-assigned and client-assigned order identifiers stay the same, queue priority in the order book is preserved where possible, and if the amended quantity drops below the already-filled quantity the remaining quantity is cancelled.

    **API Key Permissions Required:** `Orders and trades - Create & modify orders` or `Orders and trades - Cancel & close orders`

    Args:
      txid: The Kraken identifier for the order to amend. Either `txid` or `cl_ord_id` is required.
      cl_ord_id: The client identifier for the order to amend. Either `txid` or `cl_ord_id` is required.
      order_qty: The new order quantity, in terms of the base asset.
      display_qty: For `iceberg` orders only, the new quantity to show in the book while the rest of the order quantity remains hidden. Minimum value is 1/15 of the remaining order quantity.
      limit_price: The new limit price (for order types that support a limit price). May use relative pricing: `+`/`-` prefix as an offset from the reference price (e.g. `+50` or `-100`), optionally suffixed with `%`.
      trigger_price: The new trigger price (for triggered order types only). May use relative pricing: `+`/`-` prefix as an offset from the reference price, optionally suffixed with `%`.
      pair: Required on amends for non-crypto pairs, e.g. the pair symbol for xstocks.
      post_only: For `limit_price` amends only. If true, the limit price change is rejected unless it can be posted passively in the book.
      deadline: RFC3339 timestamp (e.g. `2021-04-01T00:18:45Z`) after which the matching engine should reject this amend if it is still queued due to latency, minimum now()+2s, maximum now()+60s.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/trading/amend-order)
    """
    data = {}
    if txid is not None:
      data['txid'] = txid
    if cl_ord_id is not None:
      data['cl_ord_id'] = cl_ord_id
    if order_qty is not None:
      data['order_qty'] = order_qty
    if display_qty is not None:
      data['display_qty'] = display_qty
    if limit_price is not None:
      data['limit_price'] = limit_price
    if trigger_price is not None:
      data['trigger_price'] = trigger_price
    if pair is not None:
      data['pair'] = pair
    if post_only is not None:
      data['post_only'] = post_only
    if deadline is not None:
      data['deadline'] = deadline

    return await self.authed_request(
      '/0/private/AmendOrder', data, validator=validate_amend_order
    )
