from typing_extensions import Any
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class ActivateOutcomeDeployerDeactivate(TypedDict):
  """Deactivate the caller's outcome-deployer status. Requires the minimum 183-day deployer staking duration to have elapsed and zero active outcomes. Permanent: the account cannot re-activate, and its venue name stays reserved."""

  deactivate: None
  """Marker value; carries no fields."""


class ActivateOutcomeDeployerResponse(TypedDict):
  """Successful response to ActivateOutcomeDeployer."""

  type: str
  """Echoes the action type of the request that produced this response. Almost certainly `"activateOutcomeDeployer"`, matching every other captured hyperliquid exchange endpoint's convention of echoing the request's own top-level `type` (e.g. exchange.vault_transfer's response.type is `"vaultTransfer"`) -- but left as a plain string rather than an `enum` since no example of this specific action has been observed."""
  data: dict[str, Any]
  """Action-specific result payload. Not documented at all by HIP-4's doc page. Left as an open map rather than asserted empty, since neither shape is confirmed."""


class ActivateOutcomeDeployerVenue(TypedDict):
  """New venue to activate the caller under."""

  venueName: str
  """2-4 lowercase ASCII letters naming the new outcome-deployer venue, subject to the same rules as a HIP-3 perp-DEX name. Must be unique across every deployer's venue name -- including deactivated ones, whose names stay reserved -- and must not match an existing perp-DEX name or `spot`. A registered venue name also cannot later be claimed by a HIP-3 perp-DEX deployment."""


class ActivateOutcomeDeployerActivate(TypedDict):
  """Activate the caller as a HIP-4 outcome deployer under a new venue name. Requires Standard account abstraction and a staking requirement that stacks with the deployer's other staking requirements (e.g. HIP-3) and must be maintained for as long as the account remains an outcome deployer."""

  activate: ActivateOutcomeDeployerVenue


adapter = pydantic.TypeAdapter(ExchangeResponse[ActivateOutcomeDeployerResponse])


class ActivateOutcomeDeployer(ExchangeMixin):
  async def activate_outcome_deployer(
    self,
    body: ActivateOutcomeDeployerActivate | ActivateOutcomeDeployerDeactivate,
    *,
    expires_after: int | None = None,
  ) -> ExchangeResponse[ActivateOutcomeDeployerResponse]:
    """Activate or deactivate the caller as a HIP-4 outcome/prediction-market deployer through Hyperliquid POST /exchange using action type `activateOutcomeDeployer`. Activation is the prerequisite every other `exchange.outcome_deployer.*` action depends on.

    Args:
      body: Activate or deactivate the caller as a HIP-4 outcome deployer; the two are mutually exclusive variants of one action.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-4-deployer-actions)
    """
    ts = timestamp.now()
    action: dict[str, object] = {'type': 'activateOutcomeDeployer', **body}
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
