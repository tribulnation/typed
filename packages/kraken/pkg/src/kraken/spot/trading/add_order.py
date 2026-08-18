"""`spot.trading.add_order` -- private Spot endpoint."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


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
  """Human-readable description of the order (and its conditional close, if one was attached)."""

  order: NotRequired[str]
  """Human-readable order description."""
  close: NotRequired[str]
  """Human-readable conditional close order description, if one was attached."""


class OrderAdded(TypedDict):
  """Result of placing a new order."""

  descr: NotRequired[OrderDescription]
  txid: NotRequired[list[str]]
  """Transaction ID(s) for the order -- present only once the order actually reaches the matching engine, i.e. absent when `validate` was set."""


validate_add_order = validator(OrderAdded)


class AddOrder(RpcEndpoint):
  """`spot.trading.add_order`."""

  async def add_order(
    self,
    *,
    pair: str,
    type: Literal['buy', 'sell'],
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
    ],
    volume: str,
    displayvol: str | None = None,
    userref: int | None = None,
    cl_ord_id: str | None = None,
    asset_class: Literal['tokenized_asset'] | None = None,
    price: str | None = None,
    price2: str | None = None,
    trigger: Literal['index', 'last'] | None = None,
    leverage: str | None = None,
    reduce_only: bool | None = None,
    stptype: Literal['cancel-newest', 'cancel-oldest', 'cancel-both'] | None = None,
    oflags: str | None = None,
    timeinforce: Literal['GTC', 'IOC', 'GTD', 'FOK'] | None = None,
    starttm: str | None = None,
    expiretm: str | None = None,
    close: ConditionalCloseOrder | None = None,
    deadline: str | None = None,
    validate: bool | None = None,
    broker: str | None = None,
  ) -> OrderAdded:
    """Place a new order. See `AssetPairs` for tradable pairs, their price/quantity precisions, order minimums, and available leverage.

    **API Key Permissions Required:** `Orders and trades - Create & modify orders`

    Args:
      pair: Asset pair `id` or `altname`, e.g. `XBTUSD`.
      type: Order direction.
      ordertype: The execution model of the order.
      volume: Order quantity in terms of the base asset. May be `0` for closing margin orders to automatically fill the requisite quantity.
      displayvol: For `iceberg` orders only, the quantity to show in the book while the rest of the order quantity remains hidden. Minimum value is 1/15 of `volume`.
      userref: An optional non-unique numeric identifier the client can associate with any number of orders (e.g. for grouping by pair/side/strategy), letting cancel/query calls target the group by `userref` instead of individual `txid`s. Uniqueness is not enforced. Mutually exclusive with `cl_ord_id`.
      cl_ord_id: An alphanumeric client order identifier which uniquely identifies this order for the client. One of: a long UUID (`6d1b345e-2821-40e2-ad83-4ecb18a06876`), a short UUID with no dashes, or free-form ASCII text up to 18 characters. Mutually exclusive with `userref`.
      asset_class: Required on requests for non-crypto pairs, e.g. `tokenized_asset` for xstocks.
      price: Limit price for `limit`/`iceberg` orders, or trigger price for `stop-loss`, `stop-loss-limit`, `take-profit`, `take-profit-limit`, `trailing-stop` and `trailing-stop-limit` orders. Either `price` or `price2` may be prefixed with `+`/`-` (offset from last traded price) or `#` (add or subtract depending on order direction/type), and suffixed with `%` for a relative percentage instead of an absolute difference. Trailing stops must use the `+` prefix (direction is inferred from the order's buy/sell side) and also accept the `%` suffix.
      price2: Secondary limit price for `stop-loss-limit`, `take-profit-limit` and `trailing-stop-limit` orders. For trailing stops this is a relative offset (`+`/`-` prefix, optionally `%` suffix) from the trigger price to the limit price -- `+0` sets the limit price equal to the trigger price.
      trigger: Price signal used to trigger `stop-loss`, `stop-loss-limit`, `take-profit`, `take-profit-limit`, `trailing-stop` and `trailing-stop-limit` orders, and any attached conditional close order. During connectivity issues with external index feeds, the last trade price is used as a fallback reference.
      leverage: Amount of leverage desired. Defaults to none.
      reduce_only: If true, the order will only reduce a currently open position rather than increase it or open a new one.
      stptype: Self Trade Prevention (STP) mode, defining which order(s) are expired to prevent a self-match: `cancel-newest` cancels the arriving order, `cancel-oldest` cancels the resting order, `cancel-both` cancels both.
      oflags: Comma-delimited list of order flags: `post` (post-only, available when `ordertype = limit`), `fcib` (prefer fee in base currency, default when selling), `fciq` (prefer fee in quote currency, default when buying, mutually exclusive with `fcib`), `nompp` (deprecated -- disabling Market Price Protection is no longer supported; accepted but ignored if supplied), `viqc` (order volume expressed in quote currency; buy market orders only, unavailable on margin orders).
      timeinforce: How long the order should remain in the book before being cancelled. `GTC` (good-'til-cancelled, default): rests until filled or cancelled. `IOC` (immediate-or-cancel): fills what it can immediately, cancels the remainder rather than resting. `GTD` (good-'til-date): must be paired with `expiretm`. `FOK` (fill-or-kill): fills the entire order immediately or cancels it entirely.
      starttm: Scheduled start time: `0` for now (default), an absolute unix timestamp, or `+<n>` for `<n>` seconds from now (URL-encode the `+` as `%2b`).
      expiretm: Expiry time for `GTD` orders, up to one month in the future: `0` for no expiration (default), an absolute unix timestamp, or `+<n>` for `<n>` seconds from now, minimum 5 (URL-encode the `+` as `%2b`).
      close: Conditional close order, attached to this order. Triggered by execution of the primary order in the same quantity and opposite direction, but once triggered becomes an independent order that may reduce or increase net position, not just close it.
      deadline: RFC3339 timestamp (e.g. `2021-04-01T00:18:45Z`) after which the matching engine should reject this order if it is still queued due to latency, minimum now()+2s, maximum now()+60s.
      validate: If true, the order is validated only and never reaches the matching engine (no `txid` is returned).
      broker: Broker IIBAN (partner's Kraken IIBAN).

    References:
      - [Official docs](https://docs.kraken.com/api-reference/trading/add-order)
    """
    data: dict = {
      'pair': pair,
      'type': type,
      'ordertype': ordertype,
      'volume': volume,
    }
    if displayvol is not None:
      data['displayvol'] = displayvol
    if userref is not None:
      data['userref'] = userref
    if cl_ord_id is not None:
      data['cl_ord_id'] = cl_ord_id
    if asset_class is not None:
      data['asset_class'] = asset_class
    if price is not None:
      data['price'] = price
    if price2 is not None:
      data['price2'] = price2
    if trigger is not None:
      data['trigger'] = trigger
    if leverage is not None:
      data['leverage'] = leverage
    if reduce_only is not None:
      data['reduce_only'] = reduce_only
    if stptype is not None:
      data['stptype'] = stptype
    if oflags is not None:
      data['oflags'] = oflags
    if timeinforce is not None:
      data['timeinforce'] = timeinforce
    if starttm is not None:
      data['starttm'] = starttm
    if expiretm is not None:
      data['expiretm'] = expiretm
    if close is not None:
      data['close'] = close
    if deadline is not None:
      data['deadline'] = deadline
    if validate is not None:
      data['validate'] = validate
    if broker is not None:
      data['broker'] = broker

    return await self.authed_request(
      '/0/private/AddOrder', data, validator=validate_add_order
    )
