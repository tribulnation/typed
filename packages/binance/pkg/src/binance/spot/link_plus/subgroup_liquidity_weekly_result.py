from json import dumps
from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CmMakerWeeklyResultStats(TypedDict):
  """CmMaker Liquidity Program weekly result statistics."""

  weeklyMakerVol: NotRequired[str]
  """COIN-M Futures maker trading volume over the week."""
  weeklyMakerVolExclBTC: NotRequired[str]
  """COIN-M Futures maker trading volume over the week, excluding BTC pairs."""
  weeklyMakerVolPct: NotRequired[str]
  """COIN-M Futures maker volume market-share percentage over the week."""
  weeklyMakerVolPctExclBTC: NotRequired[str]
  """COIN-M Futures maker volume market-share percentage over the week, excluding BTC pairs."""


class SpotMakerWeeklyResultStats(TypedDict):
  """SpotMaker Liquidity Program weekly result statistics."""

  weeklyMakerVol: NotRequired[str]
  """Spot maker trading volume over the week."""
  weeklyMakerVolPct: NotRequired[str]
  """Spot maker volume market-share percentage over the week."""


class UmMakerWeeklyResultStats(TypedDict):
  """UmMaker Liquidity Program weekly result statistics."""

  weeklyMakerVol: NotRequired[str]
  """USDⓈ-M Futures maker trading volume over the week."""
  weeklyMakerVolExclBTC: NotRequired[str]
  """USDⓈ-M Futures maker trading volume over the week, excluding BTC pairs."""
  weeklyMakerVolPct: NotRequired[str]
  """USDⓈ-M Futures maker volume market-share percentage over the week."""
  weeklyMakerVolPctExclBTC: NotRequired[str]
  """USDⓈ-M Futures maker volume market-share percentage over the week, excluding BTC pairs."""
  weeklyMakerVolPctUSDC: NotRequired[str]
  """USDⓈ-M Futures maker volume market-share percentage over the week, USDC-margined pairs."""


class UmTakerWeeklyResultStats(TypedDict):
  """UmTaker Liquidity Program weekly result statistics."""

  weeklyTakerVolBTC: NotRequired[str]
  """USDⓈ-M Futures taker trading volume over the week, BTC pairs."""
  weeklyTakerVolAlt: NotRequired[str]
  """USDⓈ-M Futures taker trading volume over the week, altcoin pairs."""
  weeklyTakerVolTotal: NotRequired[str]
  """USDⓈ-M Futures total taker trading volume over the week."""
  weeklyTakerVolPctBTC: NotRequired[str]
  """USDⓈ-M Futures taker volume market-share percentage over the week, BTC pairs."""
  weeklyTakerVolPctAlt: NotRequired[str]
  """USDⓈ-M Futures taker volume market-share percentage over the week, altcoin pairs."""


class CmMakerWeeklyResult(TypedDict):
  """CmMaker Liquidity Program weekly result, including the final rebate/discount."""

  weekStart: NotRequired[int]
  """Start of the result week, as milliseconds since epoch."""
  finalRebate: NotRequired[str]
  """Final COIN-M Futures maker rebate rate for the week."""
  weeklyStats: NotRequired[CmMakerWeeklyResultStats]


class SpotMakerWeeklyResult(TypedDict):
  """SpotMaker Liquidity Program weekly result, including the final rebate/discount."""

  weekStart: NotRequired[int]
  """Start of the result week, as milliseconds since epoch."""
  finalRebate: NotRequired[str]
  """Final Spot maker rebate rate for the week."""
  weeklyStats: NotRequired[SpotMakerWeeklyResultStats]


class UmMakerWeeklyResult(TypedDict):
  """UmMaker Liquidity Program weekly result, including the final rebate/discount."""

  weekStart: NotRequired[int]
  """Start of the result week, as milliseconds since epoch."""
  finalRebateUsdt: NotRequired[str]
  """Final USDⓈ-M Futures maker rebate rate for the week, USDT-margined."""
  weeklyStats: NotRequired[UmMakerWeeklyResultStats]


class UmTakerWeeklyResult(TypedDict):
  """UmTaker Liquidity Program weekly result, including the final rebate/discount."""

  weekStart: NotRequired[int]
  """Start of the result week, as milliseconds since epoch."""
  finalUsdtDiscount: NotRequired[str]
  """Final USDⓈ-M Futures taker fee discount for the week, USDT-margined."""
  finalUsdcDiscount: NotRequired[str]
  """Final USDⓈ-M Futures taker fee discount for the week, USDC-margined."""
  weeklyStats: NotRequired[UmTakerWeeklyResultStats]


class SubGroupLiquidityProgramWeeklyResultEntry(TypedDict):
  """Liquidity Program weekly result for one sub-group."""

  userId: NotRequired[int]
  """User ID of the sub-group's owning sub-account."""
  groupId: NotRequired[int]
  """Sub-group ID."""
  groupName: NotRequired[str]
  """Name of the sub-group."""
  spotMakerProgram: NotRequired[SpotMakerWeeklyResult]
  umMakerProgram: NotRequired[UmMakerWeeklyResult]
  cmMakerProgram: NotRequired[CmMakerWeeklyResult]
  umTakerProgram: NotRequired[UmTakerWeeklyResult]


class SubGroupLiquidityProgramWeeklyResult(TypedDict):
  """Liquidity Program weekly results for one or more sub-groups."""

  status: NotRequired[str]
  """Response status, e.g. `OK`."""
  type: NotRequired[str]
  """Response category, e.g. `GENERAL`."""
  code: NotRequired[str]
  """Response code; `"000000000"` on success."""
  data: NotRequired[list[SubGroupLiquidityProgramWeeklyResultEntry]]
  """One entry per queried (or active) sub-group."""


class SubgroupLiquidityWeeklyResult(RpcEndpoint):
  """Return sub-group Liquidity Program weekly results with final rebates."""

  async def subgroup_liquidity_weekly_result(
    self,
    *,
    group_id: list[int] | None = None,
    date: int | None = None,
    validate: bool | None = None,
  ) -> SubGroupLiquidityProgramWeeklyResult:
    """Return sub-group Liquidity Program weekly results with final rebates.

    Args:
      group_id: Sub-group IDs to query, up to 50. Sent as repeated `groupId` query params, e.g. `groupId=1001&groupId=1002`. Omit to query all active groups.
      date: Query a specific week, as milliseconds since epoch. Defaults to the latest data on the previous week.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-link-plus/api/rest-api/~#query-liquidity-program-weekly-results-for-sub-groups)
    """
    params = {}
    if group_id is not None:
      params['groupId'] = dumps(group_id, separators=(',', ':'))
    if date is not None:
      params['date'] = date
    _Response = SubGroupLiquidityProgramWeeklyResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/vip/liquidity-programs/subgroups/weekly-result',
      params=params,
      validator=_validator,
      validate=validate,
    )
