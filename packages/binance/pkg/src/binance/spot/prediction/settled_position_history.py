from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PredictionSettledPosition(TypedDict):
  """One settled (resolved) prediction position."""

  positionId: NotRequired[int]
  """Position ID."""
  vendor: NotRequired[str]
  """Prediction liquidity vendor backing this position."""
  chainId: NotRequired[str]
  """Chain ID this position settled on."""
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
  """Outcome shares held at settlement, as a decimal string."""
  avgPrice: NotRequired[str]
  """Average entry price, as a decimal string."""
  totalCost: NotRequired[str]
  """Total cost basis, as a decimal string."""
  value: NotRequired[str]
  """Value at settlement, as a decimal string."""
  currentPrice: NotRequired[str]
  """Settlement price, as a decimal string."""
  toWin: NotRequired[str]
  """Payout owed if this outcome resolved in this position's favor, as a decimal string."""
  positionStatus: NotRequired[str]
  """Position lifecycle status."""
  isWinner: NotRequired[bool]
  """Whether this position's outcome won."""
  redeemStatus: NotRequired[Literal['PENDING', 'CONFIRMED', 'FAILED', 'NOT_FOUND']]
  """On-chain redemption status of this position's payout."""
  endDate: NotRequired[Timestamp]
  """Time the underlying market closed for trading."""
  finalOutcome: NotRequired[str]
  """Outcome the market resolved to."""
  realizedPnl: NotRequired[str]
  """Realized profit and loss, as a decimal string."""
  pnl: NotRequired[str]
  """Realized profit and loss, as a decimal string."""
  claimAmount: NotRequired[str]
  """Amount claimed (or claimable), as a decimal string."""
  settledDate: NotRequired[Timestamp]
  """Time the underlying market settled."""
  createdTime: NotRequired[Timestamp]
  """Time this position was opened."""
  updatedTime: NotRequired[Timestamp]
  """Time this position was last updated."""


class PredictionSettledPositionHistoryResult(TypedDict):
  """This user's settled prediction position history."""

  totalCount: NotRequired[int]
  """Total number of settled positions matching the filter."""
  positions: NotRequired[list[PredictionSettledPosition]]
  """Settled positions on this page."""


class SettledPositionHistory(RpcEndpoint):
  """Get the authenticated user's settled (resolved) prediction position history with optional filters."""

  async def settled_position_history(
    self,
    *,
    wallet_address: str,
    l1category: str | None = None,
    result: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    offset: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> PredictionSettledPositionHistoryResult:
    """Get the authenticated user's settled (resolved) prediction position history with optional filters.

    Args:
      wallet_address: User's prediction wallet address.
      l1category: Filter by level-1 category.
      result: Settlement result filter.
      start_date: Start date. Format `yyyy-MM-dd`. Must be <= `endDate`.
      end_date: End date. Format `yyyy-MM-dd`. Must be >= `startDate`.
      offset: Pagination offset. Default `0`.
      limit: Page size. Default `20`, range 1-100.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/position#query-settled-position-history)
    """
    params: dict = {
      'walletAddress': wallet_address,
    }
    if l1category is not None:
      params['l1Category'] = l1category
    if result is not None:
      params['result'] = result
    if start_date is not None:
      params['startDate'] = start_date
    if end_date is not None:
      params['endDate'] = end_date
    if offset is not None:
      params['offset'] = offset
    if limit is not None:
      params['limit'] = limit
    _Response = PredictionSettledPositionHistoryResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/w3w/wallet/prediction/position/settled-history',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def settled_position_history_paged(
    self,
    *,
    wallet_address: str,
    l1category: str | None = None,
    result: int | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[PredictionSettledPositionHistoryResult]:
    """Yield successive pages of `settled_position_history`.

    Advances `offset` by `(limit if limit is not None else 20)` and stops once it has
    covered the `totalCount` items the response reports, or after `max_pages` pages when
    one is given.
    """
    offset = 0
    pages = 0
    while True:
      response = await self.settled_position_history(
        wallet_address=wallet_address,
        l1category=l1category,
        result=result,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('totalCount') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or limit is None or pages * limit >= total:
        break
      offset += limit if limit is not None else 20
