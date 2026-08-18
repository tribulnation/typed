from typing_extensions import TypedDict
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class UpdateEarnWalletRewardCurrencyRequest(TypedDict):
  rewardCurrency: str
  """Currency to obtain the reward"""


class UpdateEarnWalletRewardCurrencyResponse(TypedDict):
  result: bool
  """Whether the reward currency update succeeded."""


validate_response = validator(UpdateEarnWalletRewardCurrencyResponse)


class UpdateRewardsConfig(RpcEndpoint):
  async def update_rewards_config(
    self,
    wallet_id: str,
    update_earn_wallet_reward_currency_request: UpdateEarnWalletRewardCurrencyRequest,
    *,
    validate: bool | None = None,
  ) -> UpdateEarnWalletRewardCurrencyResponse:
    """Update wallet reward configuration for selected wallet

    Args:
      wallet_id: Wallet identifier
      update_earn_wallet_reward_currency_request: New reward currency to configure for the wallet.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/earn/PATCH/v1/earn/wallets/{walletId}/rewards/config)
    """
    return await self.authed_request(
      'PATCH',
      f'/v1/earn/wallets/{wallet_id}/rewards/config',
      json=update_earn_wallet_reward_currency_request,
      validator=validate_response,
      validate=validate,
    )
