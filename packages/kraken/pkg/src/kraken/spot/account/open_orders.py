"""`spot.account.open_orders` -- private Spot endpoint."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class OrderDescription(TypedDict):
  """Order description info."""

  pair: NotRequired[str]
  """Asset pair."""
  type: NotRequired[Literal['buy', 'sell']]
  """Type of order."""
  ordertype: NotRequired[
    Literal[
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
  ]
  """The execution model of the order."""
  price: NotRequired[str]
  """Primary price."""
  price2: NotRequired[str]
  """Secondary price."""
  leverage: NotRequired[str]
  """Amount of leverage."""
  order: NotRequired[str]
  """Order description, as human-readable text."""
  close: NotRequired[str]
  """Conditional close order description (if conditional close set)."""
  aclass: NotRequired[str]
  """Asset class of the pair."""


class OpenOrder(TypedDict):
  """One open order."""

  refid: NotRequired[str | None]
  """Referral order transaction ID that created this order."""
  userref: NotRequired[int | None]
  """Optional numeric client identifier associated with one or more orders."""
  cl_ord_id: NotRequired[str | None]
  """Optional alphanumeric client identifier associated with the order."""
  status: NotRequired[Literal['pending', 'open', 'closed', 'canceled', 'expired']]
  """Status of the order: `pending` (pending book entry), `open`, `closed`, `canceled`, or `expired`."""
  opentm: NotRequired[float]
  """Unix timestamp of when the order was placed."""
  starttm: NotRequired[float]
  """Unix timestamp of order start time (or 0 if not set)."""
  expiretm: NotRequired[float]
  """Unix timestamp of order end time (or 0 if not set)."""
  descr: NotRequired[OrderDescription]
  time_in_force: NotRequired[Literal['gtc', 'ioc', 'gtd', 'fok']]
  """Time-in-force of the order: `gtc` (good till cancelled), `ioc` (immediate or cancel), `gtd` (good till date), or `fok` (fill or kill)."""
  vol: NotRequired[str]
  """Volume of order (base currency)."""
  vol_exec: NotRequired[str]
  """Volume executed (base currency)."""
  cost: NotRequired[str]
  """Total cost (quote currency)."""
  fee: NotRequired[str]
  """Total fee (quote currency)."""
  price: NotRequired[str]
  """Average price (quote currency)."""
  stopprice: NotRequired[str]
  """Stop price (quote currency)."""
  limitprice: NotRequired[str]
  """Triggered limit price (quote currency, when limit-based order type triggered)."""
  trigger: NotRequired[Literal['last', 'index']]
  """Price signal used to trigger `stop-loss`/`take-profit`/`stop-loss-limit`/`take-profit-limit` orders. `last` is the implied trigger if this field is not set."""
  margin: NotRequired[bool]
  """Indicates if the order is funded on margin."""
  misc: NotRequired[str]
  """Comma-delimited list of miscellaneous info: `stopped` (triggered by stop price), `touched` (triggered by touch price), `liquidated`, `partial` (partial fill), `amended` (order parameters modified)."""
  sender_sub_id: NotRequired[str | None]
  """For institutional accounts, identifies the underlying sub-account/trader for Self Trade Prevention (STP)."""
  oflags: NotRequired[str]
  """Comma-delimited list of order flags: `post` (post-only, available when ordertype = limit), `fcib` (prefer fee in base currency, default if selling), `fciq` (prefer fee in quote currency, default if buying, mutually exclusive with `fcib`), `nompp` (deprecated -- accepted but ignored), `viqc` (order volume expressed in quote currency; buy market orders only, not available on margin orders)."""
  trades: NotRequired[list[str]]
  """List of trade IDs related to the order (if trades info requested and data available)."""


class OpenOrders(TypedDict):
  """Currently open orders."""

  open: NotRequired[dict[str, OpenOrder]]
  """Open orders, keyed by transaction ID."""


validate_open_orders = validator(OpenOrders)


class OpenOrdersEndpoint(RpcEndpoint):
  """`spot.account.open_orders`."""

  async def open_orders(
    self,
    *,
    trades: bool | None = None,
    userref: int | None = None,
    cl_ord_id: str | None = None,
    rebase_multiplier: Literal['rebased', 'base'] | None = None,
  ) -> OpenOrders:
    """Retrieve information about currently open orders. Returns every open order matching the given filters -- there is no pagination.

    **API Key Permissions Required:** `Orders and trades - Query open orders & trades`

    Args:
      trades: Whether or not to include trades related to position in output.
      userref: Restrict results to the given user reference id.
      cl_ord_id: Restrict results to the given client order id.
      rebase_multiplier: Optional parameter for viewing xstocks data. `rebased` displays in terms of underlying equity, `base` displays in terms of SPV tokens.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/account-data/get-open-orders)
    """
    data = {}
    if trades is not None:
      data['trades'] = trades
    if userref is not None:
      data['userref'] = userref
    if cl_ord_id is not None:
      data['cl_ord_id'] = cl_ord_id
    if rebase_multiplier is not None:
      data['rebase_multiplier'] = rebase_multiplier

    return await self.authed_request(
      '/0/private/OpenOrders', data, validator=validate_open_orders
    )
