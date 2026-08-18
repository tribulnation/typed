from .overview import Overview
from .subgroup_accounts_add import SubgroupAccountsAdd
from .subgroup_create import SubgroupCreate
from .subgroup_detail import SubgroupDetail
from .subgroup_liquidity_overview import SubgroupLiquidityOverview
from .subgroup_liquidity_performance import SubgroupLiquidityPerformance
from .subgroup_liquidity_weekly_result import SubgroupLiquidityWeeklyResult
from .subgroup_name_update import SubgroupNameUpdate


class LinkPlus(
  Overview,
  SubgroupAccountsAdd,
  SubgroupCreate,
  SubgroupDetail,
  SubgroupLiquidityOverview,
  SubgroupLiquidityPerformance,
  SubgroupLiquidityWeeklyResult,
  SubgroupNameUpdate,
):
  """Binance link_plus endpoints."""
