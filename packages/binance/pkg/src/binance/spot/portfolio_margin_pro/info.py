from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmProAccountInfo(TypedDict):
  """Portfolio Margin Pro account info."""

  uniMMR: NotRequired[str]
  """Classic Portfolio margin account maintenance margin rate."""
  accountEquity: NotRequired[str]
  """Account equity, unit: USD."""
  actualEquity: NotRequired[str]
  """Actual equity, unit: USD."""
  accountMaintMargin: NotRequired[str]
  """Classic Portfolio margin account maintenance margin, unit: USD."""
  accountInitialMargin: NotRequired[str]
  """Ignored for PM PRO and PM PRO SPAN."""
  totalAvailableBalance: NotRequired[str]
  """Ignored for PM PRO and PM PRO SPAN."""
  accountStatus: NotRequired[
    Literal[
      'NORMAL',
      'MARGIN_CALL',
      'SUPPLY_MARGIN',
      'REDUCE_ONLY',
      'ACTIVE_LIQUIDATION',
      'FORCE_LIQUIDATION',
      'BANKRUPTED',
    ]
  ]
  """Classic Portfolio margin account status."""
  accountType: NotRequired[Literal['PM_1', 'PM_2', 'PM_3']]
  """PM_1 for PM PRO, PM_2 for PM, PM_3 for PM PRO SPAN."""


class Info(RpcEndpoint):
  """Get Portfolio Margin Pro Account Info"""

  async def info(self, *, validate: bool | None = None) -> PmProAccountInfo:
    """Get Portfolio Margin Pro Account Info.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/account#get-portfolio-margin-pro-account-info)
    """
    _Response = PmProAccountInfo
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/sapi/v1/portfolio/account', validator=_validator, validate=validate
    )
