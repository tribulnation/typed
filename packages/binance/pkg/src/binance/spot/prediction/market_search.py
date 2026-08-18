from typing_extensions import Any, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PredictionMarketSearchResult(TypedDict):
  """A prediction market topic matched by search."""

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
  tradeVolume: NotRequired[str]
  """Cumulative trade volume, in collateral units, as a decimal string."""
  liquidity: NotRequired[str]
  """Current liquidity, in collateral units, as a decimal string."""
  startDate: NotRequired[Timestamp]
  """Time the topic opens for trading."""
  endDate: NotRequired[Timestamp]
  """Time the topic closes for trading."""
  status: NotRequired[str]
  """Topic lifecycle status."""
  markets: NotRequired[list[dict[str, Any]]]
  """Markets under this topic. Summarized here with no fields; see `spot.prediction.market_detail` for the full per-market shape."""


class MarketSearch(RpcEndpoint):
  """Semantic search for prediction market topics by keyword."""

  async def market_search(
    self,
    *,
    query: str,
    top_k: int | None = None,
    validate: bool | None = None,
  ) -> list[PredictionMarketSearchResult]:
    """Semantic search for prediction market topics by keyword.

    Args:
      query: Search keyword. Not blank.
      top_k: Max number of results to return. Default `20`, range 1-50.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/market-data#market-search)
    """
    params: dict = {
      'query': query,
    }
    if top_k is not None:
      params['topK'] = top_k
    _Response = list[PredictionMarketSearchResult]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/w3w/wallet/prediction/market/search',
      params=params,
      validator=_validator,
      validate=validate,
    )
