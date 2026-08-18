from typing_extensions import NotRequired, TypedDict
from bit2me.types import WalletResponse
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class TradingWalletWithdrawalRequest(TypedDict):
  toPocketId: NotRequired[str]
  """Bit2Me pocket identifier"""
  amount: str
  currency: str
  """Valid currency symbol"""


validate_response = validator(WalletResponse)


class RequestWithdrawal(RpcEndpoint):
  async def request_withdrawal(
    self,
    trading_wallet_withdrawal_request: TradingWalletWithdrawalRequest,
    *,
    validate: bool | None = None,
  ) -> WalletResponse:
    """Request a withdrawal from the Pro account to the Bit2Me wallet.

    Args:
      trading_wallet_withdrawal_request: Amount and destination Bit2Me pocket for a withdrawal from the Pro account.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-rest#tag/funding/POST/v1/trading/wallet/withdraw)
    """
    return await self.authed_request(
      'POST',
      '/v1/trading/wallet/withdraw',
      json=trading_wallet_withdrawal_request,
      validator=validate_response,
      validate=validate,
    )
