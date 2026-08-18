from typing_extensions import Any, AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PredictionMarketTopicSummary(TypedDict):
  """Summary of a prediction market topic."""

  marketTopicId: NotRequired[int]
  """Market topic ID."""
  vendor: NotRequired[str]
  """Prediction liquidity vendor backing this topic."""
  chainId: NotRequired[str]
  """Chain ID the topic settles on."""
  slug: NotRequired[str]
  """URL-friendly topic slug."""
  title: NotRequired[str]
  """Topic title."""
  question: NotRequired[str]
  """Topic question shown to users."""
  description: NotRequired[str]
  """Topic description."""
  imageUrl: NotRequired[str]
  """Topic display image URL."""
  topicType: NotRequired[str]
  """Topic layout type."""
  chartType: NotRequired[str]
  """Chart rendering type for this topic."""
  symbol: NotRequired[str]
  """Underlying price symbol this topic tracks, when applicable."""
  participantCount: NotRequired[int]
  """Number of participants in this topic."""
  collateral: NotRequired[str]
  """Collateral asset symbol."""
  feeRateBps: NotRequired[int]
  """Fee rate in basis points."""
  slippageBps: NotRequired[int]
  """Default slippage tolerance in basis points."""
  isYieldBearing: NotRequired[bool]
  """Whether the collateral backing this topic is yield-bearing."""
  tradeVolume: NotRequired[str]
  """Cumulative trade volume, in collateral units, as a decimal string."""
  liquidity: NotRequired[str]
  """Current liquidity, in collateral units, as a decimal string."""
  publishedAt: NotRequired[Timestamp]
  """Time the topic was published."""
  startDate: NotRequired[Timestamp]
  """Time the topic opens for trading."""
  endDate: NotRequired[Timestamp]
  """Time the topic closes for trading."""
  status: NotRequired[str]
  """Topic lifecycle status."""
  markets: NotRequired[list[dict[str, Any]]]
  """Markets under this topic. Summarized here with no fields; see `spot.prediction.market_detail` for the full per-market shape."""


class PredictionMarketTopicList(TypedDict):
  """Paginated list of prediction market topics."""

  marketTopics: NotRequired[list[PredictionMarketTopicSummary]]
  """Prediction market topics on this page."""
  total: NotRequired[int]
  """Total number of market topics matching the filter."""
  offset: NotRequired[int]
  """Pagination offset used for this page."""
  limit: NotRequired[int]
  """Page size used for this page."""
  hasMore: NotRequired[bool]
  """Whether further pages remain."""


class MarketList(RpcEndpoint):
  """Get a paginated list of prediction market topics, with optional category and sort filters."""

  async def market_list(
    self,
    *,
    l1category: str | None = None,
    l2category: str | None = None,
    sort_by: Literal[
      'RECOMMENDED', 'VOLUME', 'PARTICIPANTS', 'CREATED_TIME', 'END_DATE'
    ]
    | None = None,
    order_by: Literal['ASC', 'DESC'] | None = None,
    offset: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> PredictionMarketTopicList:
    """Get a paginated list of prediction market topics, with optional category and sort filters.

    Args:
      l1category: Level-1 category filter.
      l2category: Level-2 category filter.
      sort_by: Sort field.
      order_by: Sort direction.
      offset: Pagination offset. Default `0`.
      limit: Page size. Default `20`, range 1-100.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/market-data#list-prediction-markets)
    """
    params = {}
    if l1category is not None:
      params['l1Category'] = l1category
    if l2category is not None:
      params['l2Category'] = l2category
    if sort_by is not None:
      params['sortBy'] = sort_by
    if order_by is not None:
      params['orderBy'] = order_by
    if offset is not None:
      params['offset'] = offset
    if limit is not None:
      params['limit'] = limit
    _Response = PredictionMarketTopicList
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/w3w/wallet/prediction/market/list',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def market_list_paged(
    self,
    *,
    l1category: str | None = None,
    l2category: str | None = None,
    sort_by: Literal[
      'RECOMMENDED', 'VOLUME', 'PARTICIPANTS', 'CREATED_TIME', 'END_DATE'
    ]
    | None = None,
    order_by: Literal['ASC', 'DESC'] | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[PredictionMarketTopicList]:
    """Yield successive pages of `market_list`.

    Advances `offset` by `(limit if limit is not None else 20)` and stops once it has
    covered the `total` items the response reports, or after `max_pages` pages when one
    is given.
    """
    offset = 0
    pages = 0
    while True:
      response = await self.market_list(
        l1category=l1category,
        l2category=l2category,
        sort_by=sort_by,
        order_by=order_by,
        limit=limit,
        offset=offset,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or limit is None or pages * limit >= total:
        break
      offset += limit if limit is not None else 20
