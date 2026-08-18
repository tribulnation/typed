from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PredictionWallet(TypedDict):
  """One prediction wallet registered for this user."""

  walletAddress: NotRequired[str]
  """User's prediction wallet address."""
  walletId: NotRequired[str]
  """Wallet ID."""
  registeredTime: NotRequired[Timestamp]
  """Time this wallet was registered."""


class PredictionWalletList(TypedDict):
  """This user's registered prediction wallets."""

  wallets: NotRequired[list[PredictionWallet]]
  """Registered prediction wallets."""


class WalletList(RpcEndpoint):
  """Get all prediction wallets registered for the authenticated user."""

  async def wallet_list(self, *, validate: bool | None = None) -> PredictionWalletList:
    """Get all prediction wallets registered for the authenticated user.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/wallet#list-prediction-wallets)
    """
    _Response = PredictionWalletList
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/w3w/wallet/prediction/wallet/list',
      validator=_validator,
      validate=validate,
    )
