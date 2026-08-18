from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class TopUpIsolatedOnlyMarginAction(TypedDict):
  type: Literal['topUpIsolatedOnlyMargin']
  asset: int
  leverage: str


class TopUpIsolatedOnlyMarginActionResult(TypedDict):
  """Result of an accepted top-up-isolated-only-margin action."""

  type: Literal['default']
  """Discriminator confirming this is a top-up-isolated-only-margin result. The venue carries no further data alongside it."""


adapter = pydantic.TypeAdapter(ExchangeResponse[TopUpIsolatedOnlyMarginActionResult])


class TopUpIsolatedOnlyMargin(ExchangeMixin):
  async def top_up_isolated_only_margin(
    self,
    *,
    asset: int,
    leverage: str,
    vault_address: str | None = None,
    expires_after: int | None = None,
  ) -> ExchangeResponse[TopUpIsolatedOnlyMarginActionResult]:
    """Add isolated margin to reach a target leverage, through Hyperliquid POST /exchange using action type `topUpIsolatedOnlyMargin`. An alternate form of `updateIsolatedMargin` that targets a leverage value instead of a USDC amount.

    Args:
      asset: Asset index of the isolated position to top up, per `info.meta`'s `universe` ordering.
      leverage: Target leverage to reach via this top-up, as a decimal string, e.g. "3".
      vault_address: Optional vault address for the signed action.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    action: TopUpIsolatedOnlyMarginAction = {
      'type': 'topUpIsolatedOnlyMargin',
      'asset': asset,
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
