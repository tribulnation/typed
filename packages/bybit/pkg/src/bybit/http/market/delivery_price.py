"""`GET /v5/market/delivery-price` — Get Delivery Price."""

from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from bybit.core import Endpoint, validator


class DeliveryPrice(TypedDict):
  """One settled delivery."""

  symbol: str
  """Symbol name."""
  deliveryPrice: str
  """Price the contract settled at."""
  deliveryTime: str
  """Delivery time, as a millisecond timestamp."""


class DeliveryPriceResult(TypedDict):
  """Historical delivery prices."""

  category: Literal['linear', 'inverse', 'option']
  """Product type."""
  nextPageCursor: NotRequired[str]
  """Opaque cursor for the next page. Pass it back as `cursor`; an empty string means there are no further pages."""
  list: list[DeliveryPrice]
  """Deliveries, sorted by delivery time in descending order."""


adapter = validator[DeliveryPriceResult](DeliveryPriceResult)


class DeliveryPriceEndpoint(Endpoint):
  """`Get Delivery Price` — mixed into the router that owns `market.delivery_price`."""

  async def delivery_price(
    self,
    *,
    category: Literal['linear', 'inverse', 'option'],
    symbol: str | None = None,
    base_coin: str | None = None,
    settle_coin: str | None = None,
    limit: int | None = None,
    cursor: str | None = None,
    validate: bool | None = None,
  ) -> DeliveryPriceResult:
    """Get the historical delivery prices of expired futures and option contracts.

    Args:
      category: Product type.
      symbol: Symbol name in uppercase, for example `BTCUSDT`.
      base_coin: Base coin in uppercase. Applies to option only; defaults to `BTC`.
      settle_coin: Settlement coin in uppercase. Defaults to `USDC`.
      limit: Number of deliveries per page. Range [1, 200]; defaults to 50.
      cursor: Opaque pagination cursor. Pass the `nextPageCursor` returned by the previous page; omit it for the first page.
      validate: Validate the response against the generated schema.

    References:
      - [Bybit API docs](https://bybit-exchange.github.io/docs/v5/market/delivery-price)
    """
    params: dict = {
      'category': category,
    }
    if symbol is not None:
      params['symbol'] = symbol
    if base_coin is not None:
      params['baseCoin'] = base_coin
    if settle_coin is not None:
      params['settleCoin'] = settle_coin
    if limit is not None:
      params['limit'] = limit
    if cursor is not None:
      params['cursor'] = cursor
    r = await self.request('GET', '/v5/market/delivery-price', params=params)
    return self.result(r, adapter, validate)

  async def delivery_price_paged(
    self,
    *,
    category: Literal['linear', 'inverse', 'option'],
    symbol: str | None = None,
    base_coin: str | None = None,
    settle_coin: str | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[DeliveryPriceResult]:
    """Yield successive pages of `delivery_price`.

    Passes each page's token back as `cursor` and stops when a response carries no
    `nextPageCursor`, or after `max_pages` pages when one is given.
    """
    cursor: str | None = None
    pages = 0
    while True:
      response = await self.delivery_price(
        category=category,
        symbol=symbol,
        base_coin=base_coin,
        settle_coin=settle_coin,
        limit=limit,
        cursor=cursor,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      cursor = response.get('nextPageCursor')
      if not cursor:
        break
