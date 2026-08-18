from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class HaltTradingSubAction(TypedDict):
  coin: str
  isHalted: bool


class PerpDeployDefaultResponse(TypedDict):
  """Acknowledgement returned for a perpDeploy action that carries no per-item batch data."""

  type: Literal['default']
  """Fixed response-kind discriminator for this action."""


class HaltTradingAction(TypedDict):
  type: Literal['perpDeploy']
  haltTrading: HaltTradingSubAction


adapter = pydantic.TypeAdapter(ExchangeResponse[PerpDeployDefaultResponse])


class HaltTrading(ExchangeMixin):
  async def halt_trading(
    self,
    *,
    coin: str,
    is_halted: bool,
    expires_after: int | None = None,
  ) -> ExchangeResponse[PerpDeployDefaultResponse]:
    """Pause or resume trading for one asset on a HIP-3 perp dex through Hyperliquid POST /exchange using perpDeploy sub-action `haltTrading`.

    Args:
      coin: Ticker of the asset to halt or resume.
      is_halted: Whether trading should be halted (`true`) or resumed (`false`).
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions)
    """
    ts = timestamp.now()
    sub_action: HaltTradingSubAction = {
      'coin': coin,
      'isHalted': is_halted,
    }
    action: HaltTradingAction = {'type': 'perpDeploy', 'haltTrading': sub_action}
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
