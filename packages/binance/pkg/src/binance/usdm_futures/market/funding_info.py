from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FundingInfo(TypedDict):
  """One symbol's adjusted funding rate configuration."""

  symbol: str
  """Trading symbol."""
  adjustedFundingRateCap: str
  """Maximum funding rate for this symbol."""
  adjustedFundingRateFloor: str
  """Minimum funding rate for this symbol."""
  fundingIntervalHours: int
  """Hours between funding settlements for this symbol."""
  disclaimer: NotRequired[bool]
  """Ignorable flag field, kept for wire compatibility."""


class FundingInfoEndpoint(RpcEndpoint):
  """Funding rate cap/floor and interval configuration for every symbol with adjusted funding parameters."""

  async def funding_info(self, *, validate: bool | None = None) -> list[FundingInfo]:
    """Funding rate cap/floor and interval configuration for every symbol with adjusted funding parameters.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#get-funding-rate-info)
    """
    _Response = list[FundingInfo]
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET', '/fapi/v1/fundingInfo', validator=_validator, validate=validate
    )
