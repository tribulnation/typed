"""`GET /v5/market/index-price-components` — Get Index Price Components."""

from typing_extensions import TypedDict
from bybit.core import Endpoint, validator


class IndexComponent(TypedDict):
  """One constituent venue of an index."""

  exchange: str
  """Name of the constituent exchange."""
  spotPair: str
  """Spot pair quoted on that exchange."""
  equivalentPrice: str
  """Constituent price after applying `multiplier`."""
  multiplier: str
  """Multiplier applied to the constituent price."""
  price: str
  """Raw price quoted on the constituent exchange."""
  weight: str
  """Weight of the constituent in the index, as a ratio."""


class IndexPriceComponents(TypedDict):
  """Constituents behind one index price."""

  indexName: str
  """Index name."""
  lastPrice: str
  """Latest index price."""
  updateTime: str
  """Time the index was last updated, as a millisecond timestamp."""
  components: list[IndexComponent]
  """Constituent venues contributing to the index."""


adapter = validator[IndexPriceComponents](IndexPriceComponents)


class IndexPriceComponentsEndpoint(Endpoint):
  """`Get Index Price Components` — mixed into the router that owns `market.index_price_components`."""

  async def index_price_components(
    self,
    *,
    index_name: str,
    validate: bool | None = None,
  ) -> IndexPriceComponents:
    """Get the constituent exchanges and weights behind a Bybit index price.

    Args:
      index_name: Index name, for example `BTCUSDT`.
      validate: Validate the response against the generated schema.

    References:
      - [Bybit API docs](https://bybit-exchange.github.io/docs/v5/market/index-components)
    """
    params: dict = {
      'indexName': index_name,
    }
    r = await self.request('GET', '/v5/market/index-price-components', params=params)
    return self.result(r, adapter, validate)
