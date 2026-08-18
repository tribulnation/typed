from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class UsdMFuturesAccountConfig(TypedDict):
  """USD-M Futures account-level configuration."""

  feeTier: NotRequired[int]
  """Account commission tier."""
  canTrade: NotRequired[bool]
  """Whether trading is enabled."""
  canDeposit: NotRequired[bool]
  """Whether transfer-in is enabled."""
  canWithdraw: NotRequired[bool]
  """Whether transfer-out is enabled."""
  dualSidePosition: NotRequired[bool]
  """Whether hedge mode (separate LONG/SHORT positions per symbol) is enabled."""
  updateTime: NotRequired[int]
  """Reserved field, ignore."""
  multiAssetsMargin: NotRequired[bool]
  """Whether multi-assets mode is enabled."""
  tradeGroupId: NotRequired[int]
  """Trade group identifier."""


class AccountConfig(RpcEndpoint):
  """Query this account's futures configuration."""

  async def account_config(
    self,
    *,
    validate: bool | None = None,
  ) -> UsdMFuturesAccountConfig:
    """Query this account's futures configuration.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#futures-account-configuration)
    """
    _Response = UsdMFuturesAccountConfig
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/fapi/v1/accountConfig', validator=_validator, validate=validate
    )
