from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MarginAccountAsset(TypedDict):
  """One asset's margin balance."""

  asset: NotRequired[str]
  """Asset symbol."""
  borrowed: NotRequired[str]
  """Amount borrowed."""
  free: NotRequired[str]
  """Amount available."""
  interest: NotRequired[str]
  """Accrued interest owed."""
  locked: NotRequired[str]
  """Amount locked in open orders."""
  netAsset: NotRequired[str]
  """Net asset amount (free plus locked minus borrowed and interest)."""


class MarginTradeCoefficients(TypedDict):
  """Margin-call/liquidation thresholds."""

  forceLiquidationBar: NotRequired[str]
  """Margin level at which forced liquidation begins."""
  marginCallBar: NotRequired[str]
  """Margin level at which a margin call is triggered."""
  normalBar: NotRequired[str]
  """Margin level considered healthy."""


class SubAccountMarginAccount(TypedDict):
  """Margin account detail."""

  email: NotRequired[str]
  """Sub-account email."""
  marginLevel: NotRequired[str]
  """Current margin level."""
  totalAssetOfBtc: NotRequired[str]
  """Total asset value, in BTC."""
  totalLiabilityOfBtc: NotRequired[str]
  """Total liability, in BTC."""
  totalNetAssetOfBtc: NotRequired[str]
  """Total net asset value (assets minus liabilities), in BTC."""
  marginTradeCoeffVo: NotRequired[MarginTradeCoefficients]
  marginUserAssetVoList: NotRequired[list[MarginAccountAsset]]
  """Per-asset margin balances."""


class MarginAccount(RpcEndpoint):
  """Get detail on a sub-account's cross-margin account, for the master account."""

  async def __call__(
    self,
    *,
    email: str,
    validate: bool | None = None,
  ) -> SubAccountMarginAccount:
    """Get detail on a sub-account's cross-margin account, for the master account.

    Args:
      email: Sub-account email.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/asset-management#get-detail-on-sub-accounts-margin-account)
    """
    params: dict = {
      'email': email,
    }
    _Response = SubAccountMarginAccount
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/sub-account/margin/account',
      params=params,
      validator=_validator,
      validate=validate,
    )
