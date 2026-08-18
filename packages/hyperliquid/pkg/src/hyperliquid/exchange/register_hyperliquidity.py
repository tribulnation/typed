from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class Data(TypedDict):
  """Empty object accompanying `type` on every other captured non-batch exchange action on this venue; whether spotDeploy sub-actions echo it too is unconfirmed."""


class RegisterHyperliquiditySubAction(TypedDict):
  spot: int
  startPx: str
  orderSz: str
  nOrders: int
  nSeededLevels: NotRequired[int]


class DefaultResponse(TypedDict):
  """Default per-action response payload, echoed on success."""

  type: str
  """Response discriminator. Every captured non-batch exchange action on this venue returns either the literal 'default' or its own action-type string here; which applies to a spotDeploy sub-action is unconfirmed (see this endpoint's notes)."""
  data: NotRequired[Data]


class RegisterHyperliquidityAction(TypedDict):
  type: Literal['spotDeploy']
  registerHyperliquidity: RegisterHyperliquiditySubAction


adapter = pydantic.TypeAdapter(ExchangeResponse[DefaultResponse])


class RegisterHyperliquidity(ExchangeMixin):
  async def register_hyperliquidity(
    self,
    *,
    spot: int,
    start_px: str,
    order_sz: str,
    n_orders: int,
    n_seeded_levels: int | None = None,
    expires_after: int | None = None,
  ) -> ExchangeResponse[DefaultResponse]:
    """Seed hyperliquidity orders at specified price levels through Hyperliquid POST /exchange using action type `spotDeploy` with sub-action `registerHyperliquidity`. Fifth and final step of the HIP-1/HIP-2 token deployment sequence.

    Args:
      spot: The spot market index to seed (distinct from the base token index).
      start_px: Starting price for the seeded hyperliquidity orders.
      order_sz: Size of each seeded order, as a float (not wei-scaled).
      n_orders: Number of orders to seed. Must be 0 if the token's `genesis` call set `noHyperliquidity` to true.
      n_seeded_levels: Number of price levels the deployer wishes to seed with USDC instead of the token itself.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets)
    """
    ts = timestamp.now()
    sub_action: RegisterHyperliquiditySubAction = {
      'spot': spot,
      'startPx': start_px,
      'orderSz': order_sz,
      'nOrders': n_orders,
    }
    if n_seeded_levels is not None:
      sub_action['nSeededLevels'] = n_seeded_levels
    action: RegisterHyperliquidityAction = {
      'type': 'spotDeploy',
      'registerHyperliquidity': sub_action,
    }
    sig = sign_l1_action(
      action,
      wallet=self.wallet,
      nonce=ts,
      mainnet=self.mainnet,
      vault_address=None,
      expires_after=expires_after,
    )
    result = await self.client.request(
      {
        'action': action,
        'nonce': ts,
        'signature': sig,
        'vaultAddress': None,
        'expiresAfter': expires_after,
      }
    )
    return adapter.validate_python(result) if self.validate else result
