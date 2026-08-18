from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmProAccountBalance(TypedDict):
  """Balance for one asset."""

  asset: NotRequired[str]
  """Asset name."""
  totalWalletBalance: NotRequired[str]
  """Total wallet balance."""
  crossMarginAsset: NotRequired[str]
  """Cross margin asset."""
  crossMarginBorrowed: NotRequired[str]
  """Cross margin borrowed."""
  crossMarginFree: NotRequired[str]
  """Cross margin free."""
  crossMarginInterest: NotRequired[str]
  """Cross margin interest."""
  crossMarginLocked: NotRequired[str]
  """Cross margin locked."""
  umWalletBalance: NotRequired[str]
  """UM wallet balance."""
  umUnrealizedPNL: NotRequired[str]
  """UM unrealized PNL."""
  cmWalletBalance: NotRequired[str]
  """CM wallet balance."""
  cmUnrealizedPNL: NotRequired[str]
  """CM unrealized PNL."""
  updateTime: NotRequired[Timestamp]
  """Last update time."""
  negativeBalance: NotRequired[str]
  """Negative balance amount."""
  optionWalletBalance: NotRequired[str]
  """Option wallet balance."""
  optionEquity: NotRequired[str]
  """Option equity."""


class Balance(RpcEndpoint):
  """Get Portfolio Margin Pro Account Balance"""

  async def balance(
    self,
    *,
    asset: str | None = None,
    validate: bool | None = None,
  ) -> list[PmProAccountBalance]:
    """Query Portfolio Margin Pro account balance.

    Args:
      asset: Asset name.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#get-portfolio-margin-pro-account-balance)
    """
    params = {}
    if asset is not None:
      params['asset'] = asset
    _Response = list[PmProAccountBalance]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/portfolio/balance',
      params=params,
      validator=_validator,
      validate=validate,
    )
