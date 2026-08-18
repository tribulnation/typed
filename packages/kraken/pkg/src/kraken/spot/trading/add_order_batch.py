"""`spot.trading.add_order_batch` -- private Spot endpoint."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class AddOrderBatchFailure(TypedDict):
  """An order from the batch that was rejected during pre-match checks."""

  error: NotRequired[str]
  """Error description for this individual order."""


class ConditionalCloseOrder(TypedDict):
  """A conditional close order attached to a primary order."""

  ordertype: NotRequired[
    Literal[
      'limit',
      'iceberg',
      'stop-loss',
      'take-profit',
      'stop-loss-limit',
      'take-profit-limit',
      'trailing-stop',
      'trailing-stop-limit',
    ]
  ]
  """Conditional close order's execution model."""
  price: NotRequired[str]
  """Conditional close order price."""
  price2: NotRequired[str]
  """Conditional close order secondary price."""


class OrderDescription(TypedDict):
  """Human-readable description of the order."""

  order: NotRequired[str]
  """Human-readable order description."""


class AddOrderBatchSuccess(TypedDict):
  """An order from the batch that was accepted."""

  txid: NotRequired[str]
  """Transaction ID for this order."""
  descr: NotRequired[OrderDescription]


class BatchOrderSpec(TypedDict):
  """One order within an AddOrderBatch request."""

  userref: NotRequired[int]
  """An optional non-unique numeric identifier the client can associate with any number of orders (e.g. for grouping by pair/side/strategy), letting cancel/query calls target the group by `userref` instead of individual `txid`s. Uniqueness is not enforced. Mutually exclusive with `cl_ord_id`."""
  cl_ord_id: NotRequired[str]
  """An alphanumeric client order identifier which uniquely identifies this order for the client. One of: a long UUID (`6d1b345e-2821-40e2-ad83-4ecb18a06876`), a short UUID with no dashes, or free-form ASCII text up to 18 characters. Mutually exclusive with `userref`."""
  ordertype: Literal[
    'market',
    'limit',
    'iceberg',
    'stop-loss',
    'take-profit',
    'stop-loss-limit',
    'take-profit-limit',
    'trailing-stop',
    'trailing-stop-limit',
    'settle-position',
  ]
  """The execution model of the order."""
  type: Literal['buy', 'sell']
  """Order direction."""
  volume: str
  """Order quantity in terms of the base asset. May be `0` for closing margin orders to automatically fill the requisite quantity."""
  displayvol: NotRequired[str]
  """For `iceberg` orders only, the quantity to show in the book while the rest of the order quantity remains hidden. Minimum value is 1/15 of `volume`."""
  price: NotRequired[str]
  """Limit price for `limit`/`iceberg` orders, or trigger price for `stop-loss`, `stop-loss-limit`, `take-profit` and `take-profit-limit` orders. Either `price` or `price2` may be prefixed with `+`/`-` (offset from last traded price) or `#` (add or subtract depending on order direction/type), and suffixed with `%` for a relative percentage instead of an absolute difference."""
  price2: NotRequired[str]
  """Secondary limit price for `stop-loss-limit` and `take-profit-limit` orders."""
  trigger: NotRequired[Literal['index', 'last']]
  """Price signal used to trigger `stop-loss`, `stop-loss-limit`, `take-profit` and `take-profit-limit` orders. During connectivity issues with external index feeds, the last trade price is used as a fallback reference."""
  leverage: NotRequired[str]
  """Amount of leverage desired. Defaults to none."""
  reduce_only: NotRequired[bool]
  """If true, the order will only reduce a currently open position rather than increase it or open a new one."""
  stptype: NotRequired[Literal['cancel-newest', 'cancel-oldest', 'cancel-both']]
  """Self Trade Prevention (STP) mode, defining which order(s) are expired to prevent a self-match: `cancel-newest` cancels the arriving order, `cancel-oldest` cancels the resting order, `cancel-both` cancels both."""
  oflags: NotRequired[str]
  """Comma-delimited list of order flags: `post` (post-only, available when `ordertype = limit`), `fcib` (prefer fee in base currency, default when selling), `fciq` (prefer fee in quote currency, default when buying, mutually exclusive with `fcib`), `nompp` (deprecated -- disabling Market Price Protection is no longer supported; accepted but ignored if supplied), `viqc` (order volume expressed in quote currency; buy market orders only, unavailable on margin orders)."""
  timeinforce: NotRequired[Literal['GTC', 'IOC', 'GTD']]
  """How long the order should remain in the book before being cancelled. `GTC` (good-'til-cancelled, default): rests until filled or cancelled. `IOC` (immediate-or-cancel): fills what it can immediately, cancels the remainder rather than resting. `GTD` (good-'til-date): must be paired with `expiretm`."""
  starttm: NotRequired[str]
  """Scheduled start time: `0` for now (default), an absolute unix timestamp, or `+<n>` for `<n>` seconds from now."""
  expiretm: NotRequired[str]
  """Expiry time for `GTD` orders, up to one month in the future: `0` for no expiration (default), an absolute unix timestamp, or `+<n>` for `<n>` seconds from now, minimum 5."""
  close: NotRequired[ConditionalCloseOrder | None]
  """Conditional close order, attached to this order. Triggered by execution of the primary order in the same quantity and opposite direction, but once triggered becomes an independent order that may reduce or increase net position, not just close it."""


class OrderBatchAdded(TypedDict):
  """Result of submitting an order batch."""

  orders: NotRequired[list[AddOrderBatchSuccess | AddOrderBatchFailure]]
  """One result per submitted order, in request order."""


validate_add_order_batch = validator(OrderBatchAdded)


class AddOrderBatch(RpcEndpoint):
  """`spot.trading.add_order_batch`."""

  async def add_order_batch(
    self,
    *,
    orders: list[BatchOrderSpec],
    pair: str,
    asset_class: Literal['tokenized_asset'] | None = None,
    deadline: str | None = None,
    validate: bool | None = None,
    broker: str | None = None,
  ) -> OrderBatchAdded:
    """Send a batch of 2 to 15 orders, all for a single trading pair. The whole batch is validated before submission -- one invalid order rejects the batch. Once submitted, individual orders that fail pre-match checks (e.g. insufficient funds) are rejected individually and the rest of the batch is still processed.

    **API Key Permissions Required:** `Orders and trades - Create & modify orders` and `Orders and trades - Cancel & close orders`

    Args:
      orders: Orders to submit, 2 to 15 entries, all on `pair`.
      pair: Asset pair `id` or `altname` shared by every order in the batch.
      asset_class: Required on requests for non-crypto pairs, e.g. `tokenized_asset` for xstocks.
      deadline: RFC3339 timestamp (e.g. `2021-04-01T00:18:45Z`) after which the matching engine should reject this batch if it is still queued due to latency, minimum now()+2s, maximum now()+60s.
      validate: If true, orders are validated only and never reach the matching engine.
      broker: Broker IIBAN (partner's Kraken IIBAN).

    References:
      - [Official docs](https://docs.kraken.com/api-reference/trading/add-order-batch)
    """
    data: dict = {
      'orders': orders,
      'pair': pair,
    }
    if asset_class is not None:
      data['asset_class'] = asset_class
    if deadline is not None:
      data['deadline'] = deadline
    if validate is not None:
      data['validate'] = validate
    if broker is not None:
      data['broker'] = broker

    return await self.authed_json_request(
      '/0/private/AddOrderBatch', data, validator=validate_add_order_batch
    )
