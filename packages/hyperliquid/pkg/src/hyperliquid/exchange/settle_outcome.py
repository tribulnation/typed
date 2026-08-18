from typing_extensions import Any, Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class SettleOutcomeResponse(TypedDict):
  """Successful response to SettleOutcome."""

  type: str
  """Echoes the action type of the request that produced this response. On the wire this action is a variant of the outer `spotDeploy` action -- `{"type": "spotDeploy", "outcome": {"settleOutcome": {...}}}`, not its own top-level `type` (see `notes`). By analogy with every other captured hyperliquid exchange endpoint (response.type echoes the request's own top-level type), response.type most likely echoes `"spotDeploy"` here, not this action's own variant name -- but this is inferred, not observed, so it is left as a plain string rather than an `enum`."""
  data: dict[str, Any]
  """Action-specific result payload. Not documented at all by HIP-4's doc page. Left as an open map rather than asserted empty."""


class SettleOutcomeSubAction(TypedDict):
  outcome: int
  settleFraction: str
  details: Literal['']
  nameAndDescription: tuple[str, str]
  sideNames: tuple[str, str]


class SettleOutcomeWrap0(TypedDict):
  settleOutcome: SettleOutcomeSubAction


class SettleOutcomeAction(TypedDict):
  type: Literal['spotDeploy']
  outcome: SettleOutcomeWrap0


adapter = pydantic.TypeAdapter(ExchangeResponse[SettleOutcomeResponse])


class SettleOutcome(ExchangeMixin):
  async def settle_outcome(
    self,
    *,
    outcome: int,
    settle_fraction: str,
    details: Literal[''],
    name_and_description: tuple[str, str],
    side_names: tuple[str, str],
    expires_after: int | None = None,
  ) -> ExchangeResponse[SettleOutcomeResponse]:
    """Settle one outcome of the deployer through Hyperliquid POST /exchange using action type `spotDeploy`, `outcome` variant `settleOutcome`.

    Args:
      outcome: Numeric index of the outcome being settled, assigned when it was created.
      settle_fraction: Decimal string in `[0, 1]` giving the fraction of the payout the YES side receives. Standalone outcomes may settle to any fraction; question outcomes must settle to exactly `"0"` or `"1"`.
      details: Must be the empty string.
      name_and_description: Two-element `[name, description]` pair identifying the outcome or question being settled; must exactly match the outcome/question's onchain name and description.
      side_names: Two-element `[YES side name, NO side name]` pair; must exactly match the outcome's onchain side names.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-4-deployer-actions)
    """
    ts = timestamp.now()
    sub_action: SettleOutcomeSubAction = {
      'outcome': outcome,
      'settleFraction': settle_fraction,
      'details': details,
      'nameAndDescription': name_and_description,
      'sideNames': side_names,
    }
    action: SettleOutcomeAction = {
      'type': 'spotDeploy',
      'outcome': {'settleOutcome': sub_action},
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
