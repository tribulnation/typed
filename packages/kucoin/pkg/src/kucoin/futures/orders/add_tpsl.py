"""`POST /api/v1/st-orders` — Add Take Profit And Stop Loss Order."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from kucoin.types import FuturesAddOrderResult
from kucoin.core import RpcEndpoint


class FuturesAddTpslOrderLimit(TypedDict):
  """Request to place a limit futures order carrying take-profit/stop-loss triggers. At least one of `triggerStopUpPrice` (take-profit)/`triggerStopDownPrice` (stop-loss) should be given; `stopPriceType` selects the price reference both use. Choose exactly one of `size`/`qty`/`valueQty`."""

  clientOid: str
  """Client-chosen order id, unique per account, max 40 characters -- a UUID is recommended."""
  symbol: str
  """Contract symbol, e.g. `XBTUSDTM`."""
  side: Literal['buy', 'sell']
  """Order side."""
  leverage: int
  """Leverage used to calculate the margin to hold for this order. Not required when the order only closes an existing position."""
  type: Literal['limit']
  """Order type."""
  price: str
  """Limit price."""
  size: NotRequired[int]
  """Order quantity, in lots. Choose exactly one of `size`/`qty`/`valueQty`."""
  qty: NotRequired[str]
  """Order quantity, in the contract's base currency; must be an integer multiple of the contract multiplier. Choose exactly one of `size`/`qty`/`valueQty`."""
  valueQty: NotRequired[str]
  """Order quantity expressed as a value (the settlement currency of a USDS-margined contract). Choose exactly one of `size`/`qty`/`valueQty`."""
  timeInForce: NotRequired[Literal['GTC', 'IOC']]
  """Order timing strategy."""
  postOnly: NotRequired[bool]
  """Place as a post-only (maker-only) order. Invalid when `timeInForce` is `IOC`."""
  reduceOnly: NotRequired[bool]
  """Only reduce an existing position."""
  closeOrder: NotRequired[bool]
  """Close the entire current position."""
  forceHold: NotRequired[bool]
  """Force-hold this order's funds even though it reduces a position."""
  stp: NotRequired[Literal['CN', 'CO', 'CB']]
  """Self-trade prevention strategy: `CN` (cancel newest), `CO` (cancel oldest), `CB` (cancel both)."""
  marginMode: NotRequired[Literal['ISOLATED', 'CROSS']]
  """Margin mode."""
  positionSide: NotRequired[str]
  """Which side of a Hedge Mode position this order applies to. Not part of the official SDK spec (predates its sync); left as a plain string per the same reasoning as `FuturesAddOrderLimit.positionSide` (spec/schemas.json)."""
  stopPriceType: NotRequired[Literal['TP', 'MP', 'IP']]
  """Trigger price reference used by both `triggerStopUpPrice`/`triggerStopDownPrice`: `TP` (last trade price), `MP` (mark price), `IP` (index price)."""
  triggerStopUpPrice: NotRequired[str]
  """Take-profit trigger price."""
  triggerStopDownPrice: NotRequired[str]
  """Stop-loss trigger price."""
  remark: NotRequired[str]
  """Order remark, up to 100 UTF-8 characters."""


class FuturesAddTpslOrderMarket(TypedDict):
  """Request to place a market futures order carrying take-profit/stop-loss triggers. At least one of `triggerStopUpPrice` (take-profit)/`triggerStopDownPrice` (stop-loss) should be given; `stopPriceType` selects the price reference both use. Choose exactly one of `size`/`qty`/`valueQty`."""

  clientOid: str
  """Client-chosen order id, unique per account, max 40 characters -- a UUID is recommended."""
  symbol: str
  """Contract symbol, e.g. `XBTUSDTM`."""
  side: Literal['buy', 'sell']
  """Order side."""
  leverage: int
  """Leverage used to calculate the margin to hold for this order. Not required when the order only closes an existing position."""
  type: Literal['market']
  """Order type."""
  size: NotRequired[int]
  """Order quantity, in lots. Choose exactly one of `size`/`qty`/`valueQty`."""
  qty: NotRequired[str]
  """Order quantity, in the contract's base currency; must be an integer multiple of the contract multiplier. Choose exactly one of `size`/`qty`/`valueQty`."""
  valueQty: NotRequired[str]
  """Order quantity expressed as a value (the settlement currency of a USDS-margined contract). Choose exactly one of `size`/`qty`/`valueQty`."""
  reduceOnly: NotRequired[bool]
  """Only reduce an existing position."""
  closeOrder: NotRequired[bool]
  """Close the entire current position."""
  forceHold: NotRequired[bool]
  """Force-hold this order's funds even though it reduces a position."""
  stp: NotRequired[Literal['CN', 'CO', 'CB']]
  """Self-trade prevention strategy: `CN` (cancel newest), `CO` (cancel oldest), `CB` (cancel both)."""
  marginMode: NotRequired[Literal['ISOLATED', 'CROSS']]
  """Margin mode."""
  positionSide: NotRequired[str]
  """Which side of a Hedge Mode position this order applies to. Not part of the official SDK spec (predates its sync); left as a plain string per the same reasoning as `FuturesAddOrderLimit.positionSide` (spec/schemas.json)."""
  stopPriceType: NotRequired[Literal['TP', 'MP', 'IP']]
  """Trigger price reference used by both `triggerStopUpPrice`/`triggerStopDownPrice`: `TP` (last trade price), `MP` (mark price), `IP` (index price)."""
  triggerStopUpPrice: NotRequired[str]
  """Take-profit trigger price."""
  triggerStopDownPrice: NotRequired[str]
  """Stop-loss trigger price."""
  remark: NotRequired[str]
  """Order remark, up to 100 UTF-8 characters."""


_Type = FuturesAddOrderResult
adapter = validator[_Type](_Type)  # type: ignore


class AddTpsl(RpcEndpoint):
  """`Add Take Profit And Stop Loss Order` — mixed into `Orders`, the product exposing `futures.orders.add_tpsl`."""

  async def add_tpsl(
    self,
    body: FuturesAddTpslOrderLimit | FuturesAddTpslOrderMarket,
    *,
    validate: bool | None = None,
  ) -> FuturesAddOrderResult:
    """Place a limit or market order carrying take-profit and/or stop-loss trigger prices. Otherwise identical to Add: funds are held for the duration of the order once placed.

    Args:
      body: Order placement parameters, with take-profit/stop-loss triggers.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/st-orders',
      json=body,
      validator=adapter,
      validate=validate,
    )
