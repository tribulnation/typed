from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SubAccountFuturesPosition(TypedDict):
  """One USD-M futures position held by the sub-account."""

  entryPrice: NotRequired[str]
  """Average entry price."""
  leverage: NotRequired[str]
  """Position leverage."""
  maxNotional: NotRequired[str]
  """Maximum notional value allowed at the current leverage."""
  liquidationPrice: NotRequired[str]
  """Estimated liquidation price."""
  markPrice: NotRequired[str]
  """Current mark price."""
  positionAmount: NotRequired[str]
  """Signed position size (negative for short)."""
  symbol: NotRequired[str]
  """Futures symbol."""
  unrealizedProfit: NotRequired[str]
  """Unrealized profit/loss."""


class FuturesPositionRisk(RpcEndpoint):
  """Get the USD-M futures position risk of a sub-account, for the master account."""

  async def __call__(
    self,
    *,
    email: str,
    validate: bool | None = None,
  ) -> list[SubAccountFuturesPosition]:
    """Get the USD-M futures position risk of a sub-account, for the master account.

    Args:
      email: Sub-account email.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/account-management#get-futures-position-risk-of-sub-account)
    """
    params: dict = {
      'email': email,
    }
    _Response = list[SubAccountFuturesPosition]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/sub-account/futures/positionRisk',
      params=params,
      validator=_validator,
      validate=validate,
    )
