from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class UpdateLeverageAction(TypedDict):
  type: Literal['updateLeverage']
  asset: int
  isCross: bool
  leverage: int


class UpdateLeverageActionResult(TypedDict):
  """Result of an accepted update-leverage action."""

  type: Literal['default']
  """Discriminator confirming this is an update-leverage result. The venue carries no further data alongside it."""


adapter = pydantic.TypeAdapter(ExchangeResponse[UpdateLeverageActionResult])


class UpdateLeverage(ExchangeMixin):
  async def update_leverage(
    self,
    *,
    asset: int,
    is_cross: bool,
    leverage: int,
    vault_address: str | None = None,
    expires_after: int | None = None,
  ) -> ExchangeResponse[UpdateLeverageActionResult]:
    """Update cross or isolated leverage on a coin, through Hyperliquid POST /exchange using action type `updateLeverage`.

    Args:
      asset: Asset index to update leverage for, per `info.meta`'s `universe` ordering.
      is_cross: True to update cross-margin leverage, false to update isolated-margin leverage.
      leverage: New leverage value, subject to the asset's own leverage constraints.
      vault_address: Optional vault address for the signed action.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    action: UpdateLeverageAction = {
      'type': 'updateLeverage',
      'asset': asset,
      'isCross': is_cross,
      'leverage': leverage,
    }
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
