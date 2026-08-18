from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CrossMarginFeeData(TypedDict):
  """One coin's cross margin fee data at a given VIP level."""

  vipLevel: int
  """VIP level this fee data applies to."""
  coin: str
  """Coin this fee data applies to."""
  transferIn: bool
  """Whether this coin can be transferred into a cross margin account."""
  borrowable: bool
  """Whether this coin is currently borrowable on cross margin."""
  dailyInterest: str
  """Daily interest rate charged on borrowed amounts, at this VIP level."""
  yearlyInterest: str
  """Annualized interest rate charged on borrowed amounts, at this VIP level."""
  borrowLimit: str
  """Maximum amount of this coin that can be borrowed on cross margin."""
  marginablePairs: list[str]
  """Cross margin trading pairs this coin can be borrowed and traded against."""


class CrossMarginData(RpcEndpoint):
  """Get cross margin interest-rate and borrow-limit fee data, either for a given VIP level or (when `vipLevel` is omitted) this user's current specific data. Mirrors https://www.binance.com/en/margin-fee."""

  async def cross_margin_data(
    self,
    *,
    vip_level: int | None = None,
    coin: str | None = None,
    validate: bool | None = None,
  ) -> list[CrossMarginFeeData]:
    """Get cross margin interest-rate and borrow-limit fee data, either for a given VIP level or (when `vipLevel` is omitted) this user's current specific data. Mirrors https://www.binance.com/en/margin-fee.

    Args:
      vip_level: VIP level to query fee data for. Defaults to the user's own VIP level when omitted.
      coin: Coin to filter by, e.g. BNB. Omit to return fee data for every marginable coin.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/account#query-cross-margin-fee-data)
    """
    params = {}
    if vip_level is not None:
      params['vipLevel'] = vip_level
    if coin is not None:
      params['coin'] = coin
    _Response = list[CrossMarginFeeData]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/margin/crossMarginData',
      params=params,
      validator=_validator,
      validate=validate,
    )
