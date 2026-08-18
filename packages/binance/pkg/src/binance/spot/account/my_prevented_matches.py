from typing_extensions import Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PreventedMatch(TypedDict):
  """One order expired due to self-trade prevention."""

  symbol: str
  """Symbol the taker order was placed on."""
  preventedMatchId: int
  """Prevented match ID."""
  takerOrderId: int
  """ID of the order that would have taken this match."""
  makerSymbol: str
  """Symbol the maker order was placed on."""
  makerOrderId: int
  """ID of the order that would have made this match."""
  tradeGroupId: int
  """Trade group ID shared by taker and maker under the applicable self-trade prevention mode."""
  selfTradePreventionMode: Literal[
    'NONE', 'EXPIRE_MAKER', 'EXPIRE_TAKER', 'EXPIRE_BOTH', 'DECREMENT', 'TRANSFER'
  ]
  """Self-trade prevention mode that caused this match to be prevented."""
  price: str
  """Price the match would have occurred at, as a decimal string."""
  makerPreventedQuantity: str
  """Maker quantity prevented from matching, as a decimal string."""
  transactTime: int
  """Millisecond timestamp this prevented match was recorded."""


class MyPreventedMatches(RpcEndpoint):
  """Query Prevented Matches"""

  async def my_prevented_matches(
    self,
    *,
    symbol: str,
    prevented_match_id: int | None = None,
    order_id: int | None = None,
    from_prevented_match_id: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[PreventedMatch]:
    """Displays the list of this account's orders that were expired due to self-trade prevention (STP). Supported parameter combinations: `symbol` + `preventedMatchId`; `symbol` + `orderId`; `symbol` + `orderId` + `fromPreventedMatchId` (`limit` defaults to 500); `symbol` + `orderId` + `fromPreventedMatchId` + `limit`.

    Args:
      symbol: Symbol to query.
      prevented_match_id: Prevented match ID to query. See the operation description for supported parameter combinations.
      order_id: Order ID to query prevented matches for. See the operation description for supported parameter combinations.
      from_prevented_match_id: Prevented match ID to start from (inclusive), used together with `orderId`. See the operation description for supported parameter combinations.
      limit: Maximum number of prevented matches to return.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md)
    """
    params: dict = {
      'symbol': symbol,
    }
    if prevented_match_id is not None:
      params['preventedMatchId'] = prevented_match_id
    if order_id is not None:
      params['orderId'] = order_id
    if from_prevented_match_id is not None:
      params['fromPreventedMatchId'] = from_prevented_match_id
    if limit is not None:
      params['limit'] = limit
    _Response = list[PreventedMatch]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/api/v3/myPreventedMatches',
      params=params,
      validator=_validator,
      validate=validate,
    )
