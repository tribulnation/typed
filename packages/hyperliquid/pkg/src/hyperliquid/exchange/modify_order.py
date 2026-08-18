from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class LimitOrderParams(TypedDict):
  """A resting limit order, governed by a time-in-force."""

  tif: Literal['Alo', 'Ioc', 'Gtc']
  """Time-in-force: `Alo` (add-liquidity-only / post-only, rejected rather than taking liquidity), `Ioc` (immediate-or-cancel), or `Gtc` (good-til-canceled)."""


class ModifyOrderActionResult(TypedDict):
  """Result of an accepted modify action."""

  type: Literal['default']
  """Discriminator confirming this is a modify result. The venue carries no further data alongside it."""


class TriggerOrderParams(TypedDict):
  """A trigger order, guarded by a mark-price condition."""

  isMarket: bool
  """True if the trigger fires a market order; false if it fires a limit order at the order's own price."""
  triggerPx: str
  """Mark price at which the trigger fires, as a decimal string."""
  tpsl: Literal['tp', 'sl']
  """Whether this trigger order closes the position as a take-profit (`tp`) or a stop-loss (`sl`)."""


class LimitOrderType(TypedDict):
  """Order type variant for a limit order."""

  limit: LimitOrderParams


class TriggerOrderType(TypedDict):
  """Order type variant for a trigger (take-profit / stop-loss) order."""

  trigger: TriggerOrderParams


class HyperliquidOrder(TypedDict):
  a: int
  """Asset index this order trades, per `info.meta`'s `universe` ordering."""
  b: bool
  """True to buy, false to sell."""
  p: str
  """Limit price, as a decimal string."""
  s: str
  """Order size, as a decimal string."""
  r: bool
  """True to mark this order reduce-only."""
  t: LimitOrderType | TriggerOrderType
  """Order type: a resting limit order with a time-in-force, or a trigger order guarded by a mark-price condition."""
  c: NotRequired[str]
  """Caller-chosen client order id: a 128-bit hex string, e.g. `0x1234567890abcdef1234567890abcdef`."""


class ModifyOrderAction(TypedDict):
  type: Literal['modify']
  oid: int | str
  order: HyperliquidOrder
  a: NotRequired[bool]


adapter = pydantic.TypeAdapter(ExchangeResponse[ModifyOrderActionResult])


class ModifyOrder(ExchangeMixin):
  async def modify_order(
    self,
    *,
    oid: int | str,
    order: HyperliquidOrder,
    a: bool | None = None,
    vault_address: str | None = None,
    expires_after: int | None = None,
  ) -> ExchangeResponse[ModifyOrderActionResult]:
    """Modify a single resting order through Hyperliquid POST /exchange using action type `modify`.

    Args:
      oid: Order to modify: its venue-assigned order id (integer), or its client order id (128-bit hex string).
      order: The order as it should read after the modification.
      a: Always-place. When true, place the new order regardless of whether the cancel of the old one succeeded. When false (the default), the new order must be a non-trigger order with TIF `Alo`, or a non-executable order with TIF `Gtc` -- in which case its TIF is overridden to `Alo`. Omitted when false.
      vault_address: Optional vault address for the signed action.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    action: ModifyOrderAction = {
      'type': 'modify',
      'oid': oid,
      'order': order,
    }
    if a is not None:
      action['a'] = a
    sig = sign_l1_action(
      action,
      wallet=self.wallet,
      nonce=ts,
      mainnet=self.mainnet,
      vault_address=vault_address,
      expires_after=expires_after,
    )
    result = await self.client.request(
      {
        'action': action,
        'nonce': ts,
        'signature': sig,
        'vaultAddress': vault_address,
        'expiresAfter': expires_after,
      }
    )
    return adapter.validate_python(result) if self.validate else result
