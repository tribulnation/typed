from typing_extensions import NotRequired, TypedDict
from mexc.futures.core import AuthFuturesMixin
from mexc.core import validator

class TieredFeeRateData(TypedDict):
  """Current futures tiered fee rate."""
  level: int
  """Fee tier level."""
  dealAmount: float
  """Last 30 days turnover."""
  walletBalance: float
  """Yesterday wallet balance."""
  makerFee: float
  """Maker fee rate."""
  takerFee: float
  """Taker fee rate."""
  makerFeeDiscount: float
  """Maker fee discount multiplier."""
  takerFeeDiscount: float
  """Taker fee discount multiplier."""

class TieredFeeRateResponse(TypedDict):
  """Get futures tiered fee rate response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[TieredFeeRateData]

adapter = validator(TieredFeeRateResponse)

class TieredFeeRate(AuthFuturesMixin):
  async def tiered_fee_rate(
    self, *,
    symbol: str, validate: bool | None = None,
  ) -> TieredFeeRateResponse:
    """Returns the signed account tier and maker/taker fee rates for a contract.

    Args:
      symbol: Contract symbol.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#gets-the-user-39-s-current-trading-fee-rate)
    """
    headers = {}
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    r = await self.signed_request('GET', '/api/v1/private/account/tiered_fee_rate', params=params or None, headers=headers)
    return self.envelope_output(r.text, adapter, validate)
