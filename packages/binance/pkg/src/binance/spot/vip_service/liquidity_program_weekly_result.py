from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CmMakerProgramWeeklyResultStats(TypedDict):
  """Weekly COIN-M Futures maker volume statistics behind the final rebate."""

  weeklyMakerVol: NotRequired[str]
  """COIN-M Futures maker trading volume for the week."""
  weeklyMakerVolExclBTC: NotRequired[str]
  """COIN-M Futures maker trading volume for the week, excluding BTC pairs."""
  weeklyMakerVolPct: NotRequired[str]
  """COIN-M Futures maker volume for the week as a percentage of program-wide volume."""
  weeklyMakerVolPctExclBTC: NotRequired[str]
  """COIN-M Futures maker volume percentage for the week, excluding BTC pairs."""


class SpotMakerProgramWeeklyResultStats(TypedDict):
  """Weekly Spot maker volume statistics behind the final rebate."""

  weeklyMakerVol: NotRequired[str]
  """Spot maker trading volume for the week."""
  weeklyMakerVolPct: NotRequired[str]
  """Spot maker volume for the week as a percentage of program-wide volume."""


class UmMakerProgramWeeklyResultStats(TypedDict):
  """Weekly USDS-M Futures maker volume statistics behind the final rebate."""

  weeklyMakerVol: NotRequired[str]
  """USDS-M Futures maker trading volume for the week."""
  weeklyMakerVolExclBTC: NotRequired[str]
  """USDS-M Futures maker trading volume for the week, excluding BTC pairs."""
  weeklyMakerVolPct: NotRequired[str]
  """USDS-M Futures maker volume for the week as a percentage of program-wide volume."""
  weeklyMakerVolPctExclBTC: NotRequired[str]
  """USDS-M Futures maker volume percentage for the week, excluding BTC pairs."""
  weeklyMakerVolPctUSDC: NotRequired[str]
  """USDS-M Futures maker volume percentage for the week attributable to USDC pairs."""


class UmTakerProgramWeeklyResultStats(TypedDict):
  """Weekly USDS-M Futures taker volume statistics behind the final discount."""

  weeklyTakerVolBTC: NotRequired[str]
  """USDS-M Futures taker trading volume for the week in BTC pairs."""
  weeklyTakerVolAlt: NotRequired[str]
  """USDS-M Futures taker trading volume for the week in altcoin pairs."""
  weeklyTakerVolTotal: NotRequired[str]
  """USDS-M Futures taker trading volume for the week, all pairs."""
  weeklyTakerVolPctBTC: NotRequired[str]
  """USDS-M Futures taker volume percentage for the week in BTC pairs."""
  weeklyTakerVolPctAlt: NotRequired[str]
  """USDS-M Futures taker volume percentage for the week in altcoin pairs."""


class CmMakerProgramWeeklyResult(TypedDict):
  """COIN-M Futures Liquidity Program weekly result."""

  weekStart: NotRequired[int]
  """Millisecond epoch start of the evaluated week."""
  finalRebate: NotRequired[str]
  """Final COIN-M Futures maker rebate rate awarded for the week."""
  weeklyStats: NotRequired[CmMakerProgramWeeklyResultStats]


class SpotMakerProgramWeeklyResult(TypedDict):
  """Spot Liquidity Program weekly result."""

  weekStart: NotRequired[int]
  """Millisecond epoch start of the evaluated week."""
  finalRebate: NotRequired[str]
  """Final Spot maker rebate rate awarded for the week."""
  weeklyStats: NotRequired[SpotMakerProgramWeeklyResultStats]


class UmMakerProgramWeeklyResult(TypedDict):
  """USDS-M Futures Liquidity Program weekly result."""

  weekStart: NotRequired[int]
  """Millisecond epoch start of the evaluated week."""
  finalRebateUsdt: NotRequired[float]
  """Final USDS-M Futures maker rebate, denominated in USDT, awarded for the week."""
  weeklyStats: NotRequired[UmMakerProgramWeeklyResultStats]


class UmTakerProgramWeeklyResult(TypedDict):
  """USDS-M Futures Liquidity Program taker weekly result."""

  weekStart: NotRequired[int]
  """Millisecond epoch start of the evaluated week."""
  finalUsdtDiscount: NotRequired[str]
  """Final USDS-M Futures taker fee discount, denominated in USDT, awarded for the week."""
  finalUsdcDiscount: NotRequired[str]
  """Final USDS-M Futures taker fee discount, denominated in USDC, awarded for the week."""
  weeklyStats: NotRequired[UmTakerProgramWeeklyResultStats]


class LiquidityProgramWeeklyResultEntry(TypedDict):
  """Liquidity Program weekly result for one account, across all enrolled product lines."""

  userId: NotRequired[int]
  """Account user ID this entry belongs to."""
  spotMakerProgram: NotRequired[SpotMakerProgramWeeklyResult]
  umMakerProgram: NotRequired[UmMakerProgramWeeklyResult]
  cmMakerProgram: NotRequired[CmMakerProgramWeeklyResult]
  umTakerProgram: NotRequired[UmTakerProgramWeeklyResult]


class LiquidityProgramWeeklyResultsResult(TypedDict):
  """Liquidity Program weekly results."""

  status: NotRequired[str]
  """Response status, e.g. `OK`."""
  type: NotRequired[str]
  """Response category, e.g. `GENERAL`."""
  code: NotRequired[str]
  """Response code; `"000000000"` on success."""
  data: NotRequired[list[LiquidityProgramWeeklyResultEntry]]
  """Liquidity Program weekly result entries, one per account under this VIP relationship."""


class LiquidityProgramWeeklyResult(RpcEndpoint):
  """Return this user's Liquidity Program weekly results with final rebates. Updated once each weekly evaluation cycle completes, around 10:00 UTC every Monday."""

  async def liquidity_program_weekly_result(
    self,
    *,
    dt: int | None = None,
    validate: bool | None = None,
  ) -> LiquidityProgramWeeklyResultsResult:
    """Return this user's Liquidity Program weekly results with final rebates. Updated once each weekly evaluation cycle completes, around 10:00 UTC every Monday.

    Args:
      dt: Millisecond epoch date to query a specific week for. Defaults to the latest completed week's results.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-vip-service/api/rest-api/~#query-liquidity-program-weekly-results)
    """
    params = {}
    if dt is not None:
      params['dt'] = dt
    _Response = LiquidityProgramWeeklyResultsResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/vip/liquidity-programs/weekly-result',
      params=params,
      validator=_validator,
      validate=validate,
    )
