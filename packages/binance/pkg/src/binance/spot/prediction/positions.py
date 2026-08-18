from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PredictionPosition(TypedDict):
  """One prediction token position."""

  positionId: NotRequired[int]
  """Position ID."""
  vendor: NotRequired[str]
  """Prediction liquidity vendor backing this position."""
  chainId: NotRequired[str]
  """Chain ID this position settles on."""
  tokenId: NotRequired[str]
  """Prediction outcome token ID."""
  collateralSymbol: NotRequired[str]
  """Collateral asset symbol."""
  topicType: NotRequired[str]
  """Topic layout type."""
  marketTopicId: NotRequired[int]
  """Market topic ID."""
  marketId: NotRequired[int]
  """Market ID."""
  marketTopicTitle: NotRequired[str]
  """Market topic title."""
  marketTitle: NotRequired[str]
  """Market title."""
  outcomeName: NotRequired[str]
  """Outcome name held by this position."""
  outcomeIndex: NotRequired[int]
  """Zero-based outcome index."""
  shares: NotRequired[str]
  """Outcome shares held, as a decimal string."""
  avgPrice: NotRequired[str]
  """Average entry price, as a decimal string."""
  totalCost: NotRequired[str]
  """Total cost basis, as a decimal string."""
  value: NotRequired[str]
  """Current value, as a decimal string."""
  currentPrice: NotRequired[str]
  """Current market price, as a decimal string."""
  toWin: NotRequired[str]
  """Payout if this outcome resolves in this position's favor, as a decimal string."""
  positionStatus: NotRequired[str]
  """Position lifecycle status."""
  canClaim: NotRequired[bool]
  """Whether this position currently has an unclaimed payout."""
  endDate: NotRequired[Timestamp]
  """Time the underlying market closes for trading."""
  unrealizedPnl: NotRequired[str]
  """Unrealized profit and loss, as a decimal string."""
  unrealizedPnlPercent: NotRequired[str]
  """Unrealized profit and loss, as a percentage decimal string."""
  realizedPnl: NotRequired[str]
  """Realized profit and loss, as a decimal string."""
  pnl: NotRequired[str]
  """Realized plus unrealized profit and loss, as a decimal string."""
  createdTime: NotRequired[Timestamp]
  """Time this position was opened."""
  updatedTime: NotRequired[Timestamp]
  """Time this position was last updated."""


class PredictionPositionsCounts(TypedDict):
  """Position counts by status tab."""

  ongoingCount: NotRequired[int]
  """Number of ongoing (unresolved) positions."""
  endedCount: NotRequired[int]
  """Number of ended (resolved) positions."""
  pendingClaimCount: NotRequired[int]
  """Number of resolved positions with an unclaimed payout."""


class PredictionPositionsSummary(TypedDict):
  """Portfolio summary across this user's prediction positions."""

  totalValue: NotRequired[str]
  """Total current value across positions, as a decimal string."""
  positionValue: NotRequired[str]
  """Current value of open positions, as a decimal string."""
  walletBalance: NotRequired[str]
  """Prediction wallet's spendable balance, as a decimal string."""
  totalClaimableAmount: NotRequired[str]
  """Total amount currently claimable from settled positions, as a decimal string."""
  todayRealizedPnl: NotRequired[str]
  """Profit and loss realized today, as a decimal string."""
  todayRealizedPnlPercent: NotRequired[str]
  """Profit and loss realized today, as a percentage decimal string."""
  todayTotalCost: NotRequired[str]
  """Total cost basis of positions opened today, as a decimal string."""


class PredictionPositionsResult(TypedDict):
  """This user's prediction positions with a portfolio summary."""

  summary: NotRequired[PredictionPositionsSummary]
  counts: NotRequired[PredictionPositionsCounts]
  positions: NotRequired[list[PredictionPosition]]
  """Positions on this page, filtered by `tab`."""


class Positions(RpcEndpoint):
  """Get the authenticated user's prediction token positions with portfolio summary and tab-based filtering."""

  async def positions(
    self,
    *,
    wallet_address: str,
    tab: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> PredictionPositionsResult:
    """Get the authenticated user's prediction token positions with portfolio summary and tab-based filtering.

    Args:
      wallet_address: User's prediction wallet address.
      tab: Position status tab. Default `ONGOING`.
      offset: Pagination offset. Default `0`.
      limit: Page size. Default `20`, range 1-100.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/position#query-positions)
    """
    params: dict = {
      'walletAddress': wallet_address,
    }
    if tab is not None:
      params['tab'] = tab
    if offset is not None:
      params['offset'] = offset
    if limit is not None:
      params['limit'] = limit
    _Response = PredictionPositionsResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/w3w/wallet/prediction/position/list',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def positions_paged(
    self,
    *,
    wallet_address: str,
    tab: str | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[PredictionPositionsResult]:
    """Yield successive pages of `positions`.

    Advances `offset` by `len(rows)` and stops on the first page shorter than `limit`,
    or after `max_pages` pages when one is given.
    """
    offset = 0
    pages = 0
    while True:
      response = await self.positions(
        wallet_address=wallet_address,
        tab=tab,
        limit=limit,
        offset=offset,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      rows = response.get('positions') if response is not None else None
      if not rows or (limit is not None and len(rows) < limit):
        break
      offset += len(rows)
