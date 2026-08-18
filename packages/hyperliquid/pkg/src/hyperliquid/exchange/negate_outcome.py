from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class NegateOutcomeResult(TypedDict):
  type: Literal['default']
  """Response discriminator. Hyperliquid returns the generic `default` marker for this action rather than its own action type name."""


class NegateOutcomeSubAction(TypedDict):
  question: int
  outcome: int
  amount: str


class NegateOutcomeAction(TypedDict):
  type: Literal['userOutcome']
  negateOutcome: NegateOutcomeSubAction


adapter = pydantic.TypeAdapter(ExchangeResponse[NegateOutcomeResult])


class NegateOutcome(ExchangeMixin):
  async def negate_outcome(
    self,
    *,
    question: int,
    outcome: int,
    amount: str,
    expires_after: int | None = None,
  ) -> ExchangeResponse[NegateOutcomeResult]:
    """Convert X No shares of one HIP-4 outcome associated with a question into X Yes shares of every other outcome associated with that question, through Hyperliquid POST /exchange using action type `userOutcome`, variant `negateOutcome`.

    Args:
      question: Numeric index of the HIP-4 question that both the source outcome and its siblings belong to.
      outcome: Numeric index of the HIP-4 outcome whose No shares are being converted.
      amount: Decimal string amount of No shares to convert, e.g. "123.0". Produces an equal amount of Yes shares on every other outcome associated with `question`.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    sub_action: NegateOutcomeSubAction = {
      'question': question,
      'outcome': outcome,
      'amount': amount,
    }
    action: NegateOutcomeAction = {'type': 'userOutcome', 'negateOutcome': sub_action}
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
