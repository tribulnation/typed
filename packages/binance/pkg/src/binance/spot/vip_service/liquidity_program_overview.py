from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class LiquidityProgramOverviewEntry(TypedDict):
  """Liquidity Program tier and rebate rate for one account, across all enrolled product lines."""

  userId: NotRequired[int]
  """Account user ID this entry belongs to."""
  spotMakerTier: NotRequired[int]
  """Spot Liquidity Program maker tier."""
  spotMakerRebate: NotRequired[str]
  """Spot Liquidity Program maker rebate rate."""
  umMakerTier: NotRequired[int]
  """USDS-M Futures Liquidity Program maker tier."""
  umMakerRebate: NotRequired[str]
  """USDS-M Futures Liquidity Program maker rebate rate."""
  umTakerTier: NotRequired[int]
  """USDS-M Futures Liquidity Program taker tier."""
  umTakerRebate: NotRequired[str]
  """USDS-M Futures Liquidity Program taker rebate rate."""
  cmMakerTier: NotRequired[int]
  """COIN-M Futures Liquidity Program maker tier."""
  cmMakerRebate: NotRequired[str]
  """COIN-M Futures Liquidity Program maker rebate rate."""
  optionMakerTier: NotRequired[int]
  """Options Liquidity Program maker tier."""
  optionMakerRebate: NotRequired[str]
  """Options Liquidity Program maker rebate rate."""
  optionTakerTier: NotRequired[int]
  """Options Liquidity Program taker tier."""
  optionTakerRebate: NotRequired[str]
  """Options Liquidity Program taker rebate rate."""
  fiatMakerTier: NotRequired[int]
  """Fiat Liquidity Program maker tier."""
  fiatMakerRebate: NotRequired[str]
  """Fiat Liquidity Program maker rebate rate."""


class LiquidityProgramOverviewResult(TypedDict):
  """Liquidity Program overview."""

  status: NotRequired[str]
  """Response status, e.g. `OK`."""
  type: NotRequired[str]
  """Response category, e.g. `GENERAL`."""
  code: NotRequired[str]
  """Response code; `"000000000"` on success."""
  data: NotRequired[list[LiquidityProgramOverviewEntry]]
  """Liquidity Program overview entries, one per account under this VIP relationship."""


class LiquidityProgramOverview(RpcEndpoint):
  """Return this user's Liquidity Program overview: maker/taker tier and rebate rate per product line."""

  async def liquidity_program_overview(
    self,
    *,
    validate: bool | None = None,
  ) -> LiquidityProgramOverviewResult:
    """Return this user's Liquidity Program overview: maker/taker tier and rebate rate per product line.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-vip-service/api/rest-api/~#query-liquidity-program-overview)
    """
    _Response = LiquidityProgramOverviewResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/vip/liquidity-programs/overview',
      validator=_validator,
      validate=validate,
    )
