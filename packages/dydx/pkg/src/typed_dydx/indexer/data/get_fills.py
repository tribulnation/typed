"""dYdX indexer get fills types and endpoint."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typed_core import PaginatedResponse
from .. import timestamp as ts
from typing_extensions import Literal, NotRequired, TypedDict
from .core import IndexerMixin, response_parser

class Fill(TypedDict):
  """Fill payload."""
  id: str
  side: Literal['BUY', 'SELL']
  liquidity: Literal['MAKER', 'TAKER']
  type: Literal['LIMIT', 'LIQUIDATED', 'LIQUIDATION', 'DELEVERAGED', 'OFFSETTING']
  market: str
  marketType: Literal['PERPETUAL', 'SPOT']
  price: Decimal
  size: Decimal
  fee: Decimal
  affiliateRevShare: Decimal
  createdAt: datetime
  createdAtHeight: str
  orderId: NotRequired[str | None]
  clientMetadata: NotRequired[str | None]
  subaccountNumber: int
  builderFee: NotRequired[Decimal | None]
  builderAddress: NotRequired[str | None]
  positionSizeBefore: NotRequired[Decimal | None]
  entryPriceBefore: NotRequired[Decimal | None]
  positionSideBefore: NotRequired[Literal['LONG', 'SHORT'] | None]

class FillsResponse(TypedDict):
  """Fills response payload."""
  fills: list[Fill]

parse_response = response_parser(FillsResponse)

@dataclass
class GetFills(IndexerMixin):
  """Endpoint mixin for fills."""
  async def get_fills(
    self,
    address: str,
    *,
    subaccount: int,
    market: str | None = None,
    market_type: Literal['PERPETUAL', 'SPOT'] | None = None,
    created_before_or_at_height: int | None = None,
    created_before_or_at: datetime | None = None,
    limit: int | None = None,
    page: int | None = None,
    validate: bool | None = None
  ) -> FillsResponse:
    """Fetch fills for a subaccount.
  
    Args:
      address: Wallet address that owns the subaccount.
      subaccount: Subaccount number.
      market: Market ticker filter.
      market_type: Market type filter.
      created_before_or_at_height: Latest block height to include.
      created_before_or_at: Latest timestamp to include.
      limit: Maximum number of fills to return.
      page: Page number for paginated results.
      validate: Override the client response validation default for this call.
  
    Returns:
      The validated indexer response payload.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http#get-fills)
    """
    params: dict[str, object] = {
      'address': address,
      'subaccountNumber': subaccount,
    }
    if market is not None:
      params['market'] = market
    if market_type is not None:
      params['marketType'] = market_type
    if created_before_or_at_height is not None:
      params['createdBeforeOrAtHeight'] = created_before_or_at_height
    if created_before_or_at is not None:
      params['createdBeforeOrAt'] = ts.dump(created_before_or_at)
    if limit is not None:
      params['limit'] = limit
    if page is not None:
      params['page'] = page
    r = await self.request('GET', '/v4/fills', params=params)
    return parse_response(r, validate=self.validate(validate))

MarketType = Literal['PERPETUAL', 'SPOT']


@dataclass
class GetFillsPaged(GetFills):
  """Endpoint mixin for fills_paged."""
  def get_fills_paged(
    self, address: str, *,
    subaccount: int,
    market: str | None = None,
    market_type: MarketType | None = None,
    created_before_or_at_height: int | None = None,
    created_before_or_at: datetime | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> PaginatedResponse[Fill, int]:
    """Page through fills for a subaccount.
  
    Args:
      address: The wallet address that owns the account.
      subaccount: The identifier for the specific subaccount within the wallet address.
      market: The market name (e.g. `'BTC-USD'`).
      market_type: The market type (`'PERPETUAL'` or `'SPOT'`). Must be provided if `market` is provided.
      created_before_or_at_height: If given, fetches fills up to and including the given block height.
      created_before_or_at: If given, fetches fills up to and including the given timestamp.
      limit: The max. number of fills to retrieve (default: 1000, max: 1000).
      validate: Override the client response validation default for this call.
  
    Returns:
      A paginated response. Each request advances by page number until the endpoint returns no items.
  
    References:
      - [dYdX API docs](https://docs.dydx.xyz/indexer-client/http#get-fills)
    """
    async def next(page: int) -> tuple[list[Fill], int | None]:
      """Next.
    
      Args:
        page: Page number to request.
      """
      response = await self.get_fills(
        address,
        subaccount=subaccount,
        market=market,
        market_type=market_type,
        created_before_or_at_height=created_before_or_at_height,
        created_before_or_at=created_before_or_at,
        limit=limit,
        page=page,
        validate=validate,
      )
      fills = response['fills']
      next_page = page + 1 if fills else None
      return fills, next_page

    return PaginatedResponse(1, next)
