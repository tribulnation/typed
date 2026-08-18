from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class AgentEnableDexAbstractionAction(TypedDict):
  type: Literal['agentEnableDexAbstraction']


class AgentEnableDexAbstractionResult(TypedDict):
  type: Literal['default']
  """Response discriminator. Hyperliquid returns the generic `default` marker for this action rather than its own action type name."""


adapter = pydantic.TypeAdapter(ExchangeResponse[AgentEnableDexAbstractionResult])


class AgentEnableDexAbstraction(ExchangeMixin):
  async def agent_enable_dex_abstraction(
    self,
    *,
    expires_after: int | None = None,
  ) -> ExchangeResponse[AgentEnableDexAbstractionResult]:
    """Enable HIP-3 DEX abstraction through Hyperliquid POST /exchange using the L1 `agentEnableDexAbstraction` action, signed by an approved agent (API) wallet. Has the same effect as `userDexAbstraction`, but only works when transitioning the value from unset to enabled. Deprecated: prefer `agentSetAbstraction`.

    Args:
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint)
    """
    ts = timestamp.now()
    action: AgentEnableDexAbstractionAction = {
      'type': 'agentEnableDexAbstraction',
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
