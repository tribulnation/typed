"""`GET /api/v1/market/stats` — Get 24hr Stats."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class SpotStats24h(TypedDict):
  """24-hour trading statistics for one trading pair."""

  time: int
  """Snapshot timestamp, Unix ms."""
  symbol: str
  """Trading pair."""
  buy: str
  """Current best bid price."""
  sell: str
  """Current best ask price."""
  changeRate: str
  """24h price change rate (fraction)."""
  changePrice: str
  """24h absolute price change."""
  high: str
  """24h high."""
  low: str
  """24h low."""
  vol: str
  """24h volume, base currency."""
  volValue: str
  """24h volume, quote currency."""
  last: str
  """Last traded price."""
  averagePrice: str
  """24h average trade price."""
  takerFeeRate: str
  """Current base taker fee rate."""
  makerFeeRate: str
  """Current base maker fee rate."""
  takerCoefficient: str
  """Taker fee multiplier for this pair's fee category."""
  makerCoefficient: str
  """Maker fee multiplier for this pair's fee category."""


_Type = SpotStats24h
adapter = validator[_Type](_Type)  # type: ignore


class Stats24h(RpcEndpoint):
  """`Get 24hr Stats` — mixed into `Spot`, the product exposing `spot.stats_24h`."""

  async def stats_24h(
    self, *, symbol: str, validate: bool | None = None
  ) -> SpotStats24h:
    """Get 24-hour trading statistics for one trading pair.

    Args:
      symbol: Trading pair symbol, e.g. `BTC-USDT`.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
    }
    return await self.request(
      'GET',
      '/api/v1/market/stats',
      params=params,
      validator=adapter,
      validate=validate,
    )
