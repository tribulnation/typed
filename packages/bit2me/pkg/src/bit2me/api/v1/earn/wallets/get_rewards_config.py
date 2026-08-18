from bit2me.types import EarnRewardsConfigResponse
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator

validate_response = validator(EarnRewardsConfigResponse)


class GetRewardsConfig(RpcEndpoint):
  async def get_rewards_config(
    self,
    wallet_id: str,
    *,
    validate: bool | None = None,
  ) -> EarnRewardsConfigResponse:
    """Retrieves rewards configuration for selected wallet

    Args:
      wallet_id: Wallet identifier
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/earn/GET/v1/earn/wallets/{walletId}/rewards/config)
    """
    return await self.authed_request(
      'GET',
      f'/v1/earn/wallets/{wallet_id}/rewards/config',
      validator=validate_response,
      validate=validate,
    )
