"""dYdX indexer get historical funding types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typed_core import PaginatedResponse
from .. import timestamp as ts
from typing_extensions import TypedDict
from .core import IndexerMixin, response_parser

class Funding(TypedDict):
  """Funding payload."""
  ticker: str
  rate: Decimal
  price: Decimal
  effectiveAt: datetime
  effectiveAtHeight: str

class HistoricalFundingResponse(TypedDict):
  """Historical funding response payload."""
  historicalFunding: list[Funding]

parse_response = response_parser(HistoricalFundingResponse)

@dataclass
class GetHistoricalFunding(IndexerMixin):
  """Endpoint mixin for historical_funding."""
  async def get_historical_funding(
    self,
    market: str,
    *,
    effective_before_or_at: datetime | None = None,
    effective_before_or_at_height: int | None = None,
    limit: int | None = None,
    validate: bool | None = None
  ) -> HistoricalFundingResponse:
    """Fetch historical funding rates for a market.
  
    Args:
      market: Perpetual market ticker.
      effective_before_or_at: Latest effective timestamp to include.
      effective_before_or_at_height: Latest effective block height to include.
      limit: Maximum number of funding entries to return.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http#get-historical-funding)
    """
    params: dict[str, object] = {}
    if effective_before_or_at is not None:
      params['effectiveBeforeOrAt'] = ts.dump(effective_before_or_at)
    if effective_before_or_at_height is not None:
      params['effectiveBeforeOrAtHeight'] = effective_before_or_at_height
    if limit is not None:
      params['limit'] = limit
    r = await self.request('GET', f'/v4/historicalFunding/{market}', params=params)
    return parse_response(r, validate=self.validate(validate))

@dataclass
class GetHistoricalFundingPaged(GetHistoricalFunding):
  """Endpoint mixin for historical_funding_paged."""
  def get_historical_funding_paged(
    self,
    market: str,
    *,
    effective_before_or_at: datetime | None = None,
    effective_before_or_at_height: int | None = None,
    limit: int | None = None,
  ) -> PaginatedResponse[Funding, int]:
    """Page through historical funding rates for a market.
  
    Args:
      market: The market ticker (e.g. `'BTC-USD'`).
      effective_before_or_at: If given, fetches funding rates up to and including the given timestamp.
      effective_before_or_at_height: If given, fetches funding rates up to and including the given block height.
      limit: The max. number of candles to retrieve (default: 1000, max: 1000).
  
    Returns:
      A paginated response. Each request advances by the last returned funding block height until no newer page is available.
    """
    last_block = effective_before_or_at_height or -1
    async def next(last_block: int | None) -> tuple[list[Funding], int | None]:
      """Next.
    
      Args:
        last_block: Last block.
      """
      if last_block == -1:
        last_block = None
      response = await self.get_historical_funding(
        market,
        effective_before_or_at=effective_before_or_at,
        effective_before_or_at_height=last_block,
        limit=limit,
      )
      historical_funding = response['historicalFunding']
      if not historical_funding:
        return [], None
      else:
        new_last_block = int(historical_funding[-1]['effectiveAtHeight'])
        if new_last_block == last_block:
          return [], None
    
      return historical_funding, new_last_block

    return PaginatedResponse(last_block, next)
