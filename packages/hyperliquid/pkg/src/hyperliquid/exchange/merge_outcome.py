from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class MergeOutcomeResult(TypedDict):
  type: Literal['default']
  """Response discriminator. Hyperliquid returns the generic `default` marker for this action rather than its own action type name."""


class MergeOutcomeSubAction(TypedDict):
  outcome: int
  amount: str | None


class MergeOutcomeAction(TypedDict):
  type: Literal['userOutcome']
  mergeOutcome: MergeOutcomeSubAction


adapter = pydantic.TypeAdapter(ExchangeResponse[MergeOutcomeResult])


class MergeOutcome(ExchangeMixin):
  async def merge_outcome(
    self,
    *,
    outcome: int,
    amount: str | None,
    expires_after: int | None = None,
  ) -> ExchangeResponse[MergeOutcomeResult]:
    """Merge X Yes and X No shares of a HIP-4 outcome back into X quote tokens, through Hyperliquid POST /exchange using action type `userOutcome`, variant `mergeOutcome`.

    Args:
      outcome: Numeric index of the HIP-4 outcome to merge, assigned when it was created.
      amount: Decimal string amount of Yes and No shares to merge back into quote token, e.g. "123.0". Null merges the caller's full matched Yes/No balance for this outcome.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    sub_action: MergeOutcomeSubAction = {
      'outcome': outcome,
      'amount': amount,
    }
    action: MergeOutcomeAction = {'type': 'userOutcome', 'mergeOutcome': sub_action}
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
