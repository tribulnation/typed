from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class ValidatorL1streamAction(TypedDict):
  type: Literal['validatorL1Stream']
  riskFreeRate: str


class ValidatorL1streamResult(TypedDict):
  type: Literal['default']
  """Response discriminator. Hyperliquid returns the generic `default` marker for this action rather than its own action type name."""


adapter = pydantic.TypeAdapter(ExchangeResponse[ValidatorL1streamResult])


class ValidatorL1Stream(ExchangeMixin):
  async def validator_l1_stream(
    self,
    *,
    risk_free_rate: str,
    expires_after: int | None = None,
  ) -> ExchangeResponse[ValidatorL1streamResult]:
    """Cast a validator's vote on the risk-free rate used for the aligned quote asset, through Hyperliquid POST /exchange using the L1 `validatorL1Stream` action. Only callable by an active validator.

    Args:
      risk_free_rate: Risk-free rate vote, as a decimal string (e.g. "0.04" for 4%).
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    action: ValidatorL1streamAction = {
      'type': 'validatorL1Stream',
      'riskFreeRate': risk_free_rate,
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
