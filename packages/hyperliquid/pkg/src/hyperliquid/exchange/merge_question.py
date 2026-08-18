from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class MergeQuestionResult(TypedDict):
  type: Literal['default']
  """Response discriminator. Hyperliquid returns the generic `default` marker for this action rather than its own action type name."""


class MergeQuestionSubAction(TypedDict):
  question: int
  amount: str | None


class MergeQuestionAction(TypedDict):
  type: Literal['userOutcome']
  mergeQuestion: MergeQuestionSubAction


adapter = pydantic.TypeAdapter(ExchangeResponse[MergeQuestionResult])


class MergeQuestion(ExchangeMixin):
  async def merge_question(
    self,
    *,
    question: int,
    amount: str | None,
    expires_after: int | None = None,
  ) -> ExchangeResponse[MergeQuestionResult]:
    """Merge X Yes shares from each outcome associated with the same HIP-4 question into X quote tokens, through Hyperliquid POST /exchange using action type `userOutcome`, variant `mergeQuestion`.

    Args:
      question: Numeric index of the HIP-4 question to merge, assigned when it was created.
      amount: Decimal string amount of Yes shares to merge from each of the question's outcomes into quote token, e.g. "123.0". Null merges the caller's full matched Yes-share balance across the question's outcomes.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    sub_action: MergeQuestionSubAction = {
      'question': question,
      'amount': amount,
    }
    action: MergeQuestionAction = {'type': 'userOutcome', 'mergeQuestion': sub_action}
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
