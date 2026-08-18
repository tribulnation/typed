from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmUserCommissionRateForUm(TypedDict):
  """Get User Commission Rate for UM."""

  symbol: NotRequired[str]
  """Trade symbol, if existing."""
  makerCommissionRate: NotRequired[str]
  """0.02%."""
  takerCommissionRate: NotRequired[str]
  """0.04%."""


class UmCommissionRate(RpcEndpoint):
  """Get User Commission Rate for UM"""

  async def um_commission_rate(
    self,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> PmUserCommissionRateForUm:
    """Get User Commission Rate for UM.

    Args:
      symbol: Symbol.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-user-commission-rate-for-um)
    """
    params: dict = {
      'symbol': symbol,
    }
    _Response = PmUserCommissionRateForUm
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/um/commissionRate',
      params=params,
      validator=_validator,
      validate=validate,
    )
