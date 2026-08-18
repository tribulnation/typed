"""`public/get_delivery_prices` — `public/get_delivery_prices`."""

from typing_extensions import AsyncIterator, Literal, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class DeliveryPrice(TypedDict):
  """The delivery price for one settlement date."""

  date: str
  """The event date with year, month and day"""
  delivery_price: float
  """The settlement price for the instrument. Only when `state = closed`"""


class DeliveryPrices(TypedDict):
  """A page of historical delivery prices."""

  records_total: float
  """Available delivery prices"""
  data: list[DeliveryPrice]
  """Delivery prices for this page, most recent first."""


validate_get_delivery_prices = validator[DeliveryPrices](DeliveryPrices)


class GetDeliveryPrices(RpcEndpoint):
  """`public/get_delivery_prices`."""

  async def get_delivery_prices(
    self,
    *,
    index_name: Literal[
      'btc_usd',
      'eth_usd',
      'ada_usdc',
      'algo_usdc',
      'avax_usdc',
      'bch_usdc',
      'bnb_usdc',
      'btc_usdc',
      'btcdvol_usdc',
      'buidl_usdc',
      'doge_usdc',
      'dot_usdc',
      'eurr_usdc',
      'eth_usdc',
      'ethdvol_usdc',
      'hype_usdc',
      'link_usdc',
      'ltc_usdc',
      'near_usdc',
      'paxg_usdc',
      'shib_usdc',
      'sol_usdc',
      'steth_usdc',
      'ton_usdc',
      'trump_usdc',
      'trx_usdc',
      'uni_usdc',
      'usde_usdc',
      'usyc_usdc',
      'xrp_usdc',
      'btc_usdt',
      'eth_usdt',
      'eurr_usdt',
      'sol_usdt',
      'steth_usdt',
      'usdc_usdt',
      'usde_usdt',
      'btc_eurr',
      'btc_usde',
      'btc_usyc',
      'eth_btc',
      'eth_eurr',
      'eth_usde',
      'eth_usyc',
      'steth_eth',
      'paxg_btc',
      'drbfix-btc_usdc',
      'drbfix-eth_usdc',
    ],
    offset: int | None = None,
    count: int | None = None,
    validate: bool | None = None,
  ) -> DeliveryPrices:
    """Retrieves historical delivery prices for a given index. Delivery prices are the settlement prices used when futures or options contracts expire and are settled.

    Results can be paginated using the `offset` and `count` parameters. This method is useful for analyzing historical settlement prices and understanding how contracts have been settled over time.

    Args:
      index_name: Index identifier, matches (base) cryptocurrency with quote currency
      offset: The offset for pagination, default - `0`
      count: Number of requested items, default - `10`, maximum - `1000`
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/market-data/public-get_delivery_prices)
    """
    params: dict = {
      'index_name': index_name,
    }
    if offset is not None:
      params['offset'] = offset
    if count is not None:
      params['count'] = count
    return await self.request(
      'public/get_delivery_prices',
      params=params,
      validator=validate_get_delivery_prices,
      validate=validate,
    )

  async def get_delivery_prices_paged(
    self,
    *,
    index_name: Literal[
      'btc_usd',
      'eth_usd',
      'ada_usdc',
      'algo_usdc',
      'avax_usdc',
      'bch_usdc',
      'bnb_usdc',
      'btc_usdc',
      'btcdvol_usdc',
      'buidl_usdc',
      'doge_usdc',
      'dot_usdc',
      'eurr_usdc',
      'eth_usdc',
      'ethdvol_usdc',
      'hype_usdc',
      'link_usdc',
      'ltc_usdc',
      'near_usdc',
      'paxg_usdc',
      'shib_usdc',
      'sol_usdc',
      'steth_usdc',
      'ton_usdc',
      'trump_usdc',
      'trx_usdc',
      'uni_usdc',
      'usde_usdc',
      'usyc_usdc',
      'xrp_usdc',
      'btc_usdt',
      'eth_usdt',
      'eurr_usdt',
      'sol_usdt',
      'steth_usdt',
      'usdc_usdt',
      'usde_usdt',
      'btc_eurr',
      'btc_usde',
      'btc_usyc',
      'eth_btc',
      'eth_eurr',
      'eth_usde',
      'eth_usyc',
      'steth_eth',
      'paxg_btc',
      'drbfix-btc_usdc',
      'drbfix-eth_usdc',
    ],
    count: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[DeliveryPrices]:
    """Yield successive pages of `get_delivery_prices`.

    Advances `offset` by `(count if count is not None else 10)` and stops once it has
    covered the `records_total` items the response reports, or after `max_pages` pages
    when one is given.
    """
    offset = 0
    pages = 0
    while True:
      response = await self.get_delivery_prices(
        index_name=index_name, count=count, offset=offset, validate=validate
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('records_total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or count is None or pages * count >= total:
        break
      offset += count if count is not None else 10
