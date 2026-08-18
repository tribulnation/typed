from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CmMakerProgramDailyStats(TypedDict):
  """Trailing 24-hour COIN-M Futures maker statistics."""

  makerVol24h: NotRequired[str]
  """Trailing 24-hour COIN-M Futures maker trading volume."""
  makerVol24hExclBTC: NotRequired[str]
  """Trailing 24-hour COIN-M Futures maker trading volume, excluding BTC pairs."""
  makerVol24hPct: NotRequired[str]
  """Trailing 24-hour COIN-M Futures maker volume as a percentage of program-wide volume."""
  makerVol24hPctExclBTC: NotRequired[str]
  """Trailing 24-hour COIN-M Futures maker volume percentage, excluding BTC pairs."""


class CmMakerProgramWeeklyStats(TypedDict):
  """Trailing weekly COIN-M Futures maker statistics."""

  weeklyMakerVol: NotRequired[str]
  """Trailing weekly COIN-M Futures maker trading volume."""
  weeklyMakerVolExclBTC: NotRequired[str]
  """Trailing weekly COIN-M Futures maker trading volume, excluding BTC pairs."""
  weeklyMakerVolPct: NotRequired[str]
  """Trailing weekly COIN-M Futures maker volume as a percentage of program-wide volume."""
  weeklyMakerVolPctExclBTC: NotRequired[str]
  """Trailing weekly COIN-M Futures maker volume percentage, excluding BTC pairs."""


class SpotMakerProgramDailyStats(TypedDict):
  """Trailing 24-hour Spot maker statistics."""

  makerVol24h: NotRequired[str]
  """Trailing 24-hour Spot maker trading volume."""
  makerVol24hPct: NotRequired[str]
  """Trailing 24-hour Spot maker volume as a percentage of program-wide volume."""


class SpotMakerProgramWeeklyStats(TypedDict):
  """Trailing weekly Spot maker statistics."""

  weeklyMakerVol: NotRequired[str]
  """Trailing weekly Spot maker trading volume."""
  weeklyMakerVolPct: NotRequired[str]
  """Trailing weekly Spot maker volume as a percentage of program-wide volume."""


class UmMakerProgramDailyStats(TypedDict):
  """Trailing 24-hour USDS-M Futures maker statistics."""

  makerVol24h: NotRequired[str]
  """Trailing 24-hour USDS-M Futures maker trading volume."""
  makerVol24hExclBTC: NotRequired[str]
  """Trailing 24-hour USDS-M Futures maker trading volume, excluding BTC pairs."""
  makerVol24hPct: NotRequired[str]
  """Trailing 24-hour USDS-M Futures maker volume as a percentage of program-wide volume."""
  makerVol24hPctExclBTC: NotRequired[str]
  """Trailing 24-hour USDS-M Futures maker volume percentage, excluding BTC pairs."""
  makerVol24hPctUSDC: NotRequired[str]
  """Trailing 24-hour USDS-M Futures maker volume percentage attributable to USDC pairs."""


class UmMakerProgramWeeklyStats(TypedDict):
  """Trailing weekly USDS-M Futures maker statistics."""

  weeklyMakerVol: NotRequired[str]
  """Trailing weekly USDS-M Futures maker trading volume."""
  weeklyMakerVolExclBTC: NotRequired[str]
  """Trailing weekly USDS-M Futures maker trading volume, excluding BTC pairs."""
  weeklyMakerVolPct: NotRequired[str]
  """Trailing weekly USDS-M Futures maker volume as a percentage of program-wide volume."""
  weeklyMakerVolPctExclBTC: NotRequired[str]
  """Trailing weekly USDS-M Futures maker volume percentage, excluding BTC pairs."""
  weeklyMakerVolPctUSDC: NotRequired[str]
  """Trailing weekly USDS-M Futures maker volume percentage attributable to USDC pairs."""


class UmTakerProgramDailyStats(TypedDict):
  """Trailing 24-hour USDS-M Futures taker statistics."""

  takerVol24hBTC: NotRequired[str]
  """Trailing 24-hour USDS-M Futures taker trading volume in BTC pairs."""
  takerVol24hAlt: NotRequired[str]
  """Trailing 24-hour USDS-M Futures taker trading volume in altcoin pairs."""
  takerVol24hTotal: NotRequired[str]
  """Trailing 24-hour USDS-M Futures taker trading volume, all pairs."""
  takerVol24hPctBTC: NotRequired[str]
  """Trailing 24-hour USDS-M Futures taker volume percentage in BTC pairs."""
  takerVol24hPctAlt: NotRequired[str]
  """Trailing 24-hour USDS-M Futures taker volume percentage in altcoin pairs."""


class UmTakerProgramWeeklyStats(TypedDict):
  """Trailing weekly USDS-M Futures taker statistics."""

  weeklyTakerVolBTC: NotRequired[str]
  """Trailing weekly USDS-M Futures taker trading volume in BTC pairs."""
  weeklyTakerVolAlt: NotRequired[str]
  """Trailing weekly USDS-M Futures taker trading volume in altcoin pairs."""
  weeklyTakerVolTotal: NotRequired[str]
  """Trailing weekly USDS-M Futures taker trading volume, all pairs."""
  weeklyTakerVolPctBTC: NotRequired[str]
  """Trailing weekly USDS-M Futures taker volume percentage in BTC pairs."""
  weeklyTakerVolPctAlt: NotRequired[str]
  """Trailing weekly USDS-M Futures taker volume percentage in altcoin pairs."""


class CmMakerProgramPerformance(TypedDict):
  """COIN-M Futures Liquidity Program maker performance."""

  date: NotRequired[int]
  """Millisecond epoch date this snapshot covers."""
  dailyStats: NotRequired[CmMakerProgramDailyStats]
  weeklyStats: NotRequired[CmMakerProgramWeeklyStats]


class SpotMakerProgramPerformance(TypedDict):
  """Spot Liquidity Program maker performance."""

  date: NotRequired[int]
  """Millisecond epoch date this snapshot covers."""
  dailyStats: NotRequired[SpotMakerProgramDailyStats]
  weeklyStats: NotRequired[SpotMakerProgramWeeklyStats]


class UmMakerProgramPerformance(TypedDict):
  """USDS-M Futures Liquidity Program maker performance."""

  date: NotRequired[int]
  """Millisecond epoch date this snapshot covers."""
  dailyStats: NotRequired[UmMakerProgramDailyStats]
  weeklyStats: NotRequired[UmMakerProgramWeeklyStats]


class UmTakerProgramPerformance(TypedDict):
  """USDS-M Futures Liquidity Program taker performance."""

  date: NotRequired[int]
  """Millisecond epoch date this snapshot covers."""
  dailyStats: NotRequired[UmTakerProgramDailyStats]
  weeklyStats: NotRequired[UmTakerProgramWeeklyStats]


class LiquidityProgramPerformanceEntry(TypedDict):
  """Liquidity Program performance for one account, across all enrolled product lines."""

  userId: NotRequired[int]
  """Account user ID this entry belongs to."""
  spotMakerProgram: NotRequired[SpotMakerProgramPerformance]
  umMakerProgram: NotRequired[UmMakerProgramPerformance]
  cmMakerProgram: NotRequired[CmMakerProgramPerformance]
  umTakerProgram: NotRequired[UmTakerProgramPerformance]


class LiquidityProgramPerformanceResult(TypedDict):
  """Liquidity Program performance."""

  status: NotRequired[str]
  """Response status, e.g. `OK`."""
  type: NotRequired[str]
  """Response category, e.g. `GENERAL`."""
  code: NotRequired[str]
  """Response code; `"000000000"` on success."""
  data: NotRequired[list[LiquidityProgramPerformanceEntry]]
  """Liquidity Program performance entries, one per account under this VIP relationship."""


class LiquidityProgramPerformance(RpcEndpoint):
  """Return this user's Liquidity Program performance with daily and weekly statistics, per enrolled product line."""

  async def liquidity_program_performance(
    self,
    *,
    dt: int | None = None,
    validate: bool | None = None,
  ) -> LiquidityProgramPerformanceResult:
    """Return this user's Liquidity Program performance with daily and weekly statistics, per enrolled product line.

    Args:
      dt: Millisecond epoch date to query a specific day's statistics for. Defaults to the latest available data, i.e. yesterday.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-vip-service/api/rest-api/~#query-liquidity-program-performance)
    """
    params = {}
    if dt is not None:
      params['dt'] = dt
    _Response = LiquidityProgramPerformanceResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/vip/liquidity-programs/performance',
      params=params,
      validator=_validator,
      validate=validate,
    )
