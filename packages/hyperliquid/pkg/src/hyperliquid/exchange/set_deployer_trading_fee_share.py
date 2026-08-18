from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.core import timestamp
from hyperliquid.exchange.core import ExchangeMixin, ExchangeResponse, sign_l1_action


class Data(TypedDict):
  """Empty object accompanying `type` on every other captured non-batch exchange action on this venue; whether spotDeploy sub-actions echo it too is unconfirmed."""


class SetDeployerTradingFeeShareSubAction(TypedDict):
  token: int
  share: str


class DefaultResponse(TypedDict):
  """Default per-action response payload, echoed on success."""

  type: str
  """Response discriminator. Every captured non-batch exchange action on this venue returns either the literal 'default' or its own action-type string here; which applies to a spotDeploy sub-action is unconfirmed (see this endpoint's notes)."""
  data: NotRequired[Data]


class SetDeployerTradingFeeShareAction(TypedDict):
  type: Literal['spotDeploy']
  setDeployerTradingFeeShare: SetDeployerTradingFeeShareSubAction


adapter = pydantic.TypeAdapter(ExchangeResponse[DefaultResponse])


class SetDeployerTradingFeeShare(ExchangeMixin):
  async def set_deployer_trading_fee_share(
    self,
    *,
    token: int,
    share: str,
    expires_after: int | None = None,
  ) -> ExchangeResponse[DefaultResponse]:
    """Set the deployer's trading fee share for a deployed token through Hyperliquid POST /exchange using action type `spotDeploy` with sub-action `setDeployerTradingFeeShare`. Optional; may be sent at any point after `registerToken2`. The fee share defaults to 100% and this action may be resent multiple times, but only to decrease it, never to increase it.

    Args:
      token: Index of the deployed token whose trading fee share is being set.
      share: The deployer trading fee share, as a percentage string in range ['0%', '100%'] (e.g. '0.012%', '99.4%'). May only decrease from its current value.
      expires_after: Optional expiration timestamp for the signed action.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets)
    """
    ts = timestamp.now()
    sub_action: SetDeployerTradingFeeShareSubAction = {
      'token': token,
      'share': share,
    }
    action: SetDeployerTradingFeeShareAction = {
      'type': 'spotDeploy',
      'setDeployerTradingFeeShare': sub_action,
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
