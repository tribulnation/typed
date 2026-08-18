from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class AgentSetAbstractionAction(TypedDict):
  type: Literal['agentSetAbstraction']
  abstraction: Literal['i', 'u', 'p']


class AgentSetAbstractionResult(TypedDict):
  type: Literal['default']
  """Response discriminator. Hyperliquid returns the generic `default` marker for this action rather than its own action type name."""


adapter = pydantic.TypeAdapter(ExchangeResponse[AgentSetAbstractionResult])


class AgentSetAbstraction(ExchangeMixin):
  async def agent_set_abstraction(
    self,
    *,
    abstraction: Literal['i', 'u', 'p'],
    expires_after: int | None = None,
  ) -> ExchangeResponse[AgentSetAbstractionResult]:
    """Set the caller's account-abstraction mode through Hyperliquid POST /exchange using the L1 `agentSetAbstraction` action, signed by an approved agent (API) wallet.

    Args:
      abstraction: Account-abstraction mode to set, as a single-letter code: `i` is `disabled`, `u` is `unifiedAccount`, `p` is `portfolioMargin`.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    action: AgentSetAbstractionAction = {
      'type': 'agentSetAbstraction',
      'abstraction': abstraction,
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
