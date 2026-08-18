"""`spot.market_data.asset_pairs` -- public Spot market data."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class AssetPair(TypedDict):
  """One tradable asset pair's info."""

  altname: NotRequired[str]
  """Alternate pair name."""
  wsname: NotRequired[str]
  """WebSocket pair name (if available)."""
  aclass_base: NotRequired[str]
  """Asset class of the base component."""
  base: NotRequired[str]
  """Asset id of the base component."""
  aclass_quote: NotRequired[str]
  """Asset class of the quote component."""
  quote: NotRequired[str]
  """Asset id of the quote component."""
  execution_venue: NotRequired[Literal['international', 'bitnomial_exchange']]
  """Execution venue where the order book for this pair is listed."""
  lot: NotRequired[str]
  """Volume lot size."""
  pair_decimals: NotRequired[int]
  """Number of decimal places for prices in this pair."""
  cost_decimals: NotRequired[int]
  """Number of decimal places for cost of trades in the pair (quote asset terms)."""
  lot_decimals: NotRequired[int]
  """Number of decimal places for volume (base asset terms)."""
  lot_multiplier: NotRequired[int]
  """Amount to multiply lot volume by to get currency volume."""
  leverage_buy: NotRequired[list[int]]
  """Leverage amounts available when buying."""
  leverage_sell: NotRequired[list[int]]
  """Leverage amounts available when selling."""
  fees: NotRequired[list[tuple[float, float]]]
  """Taker fee schedule."""
  fees_maker: NotRequired[list[tuple[float, float]]]
  """Maker fee schedule, if the pair is on maker/taker fees."""
  fee_volume_currency: NotRequired[str]
  """Volume discount currency."""
  margin_call: NotRequired[int]
  """Margin call level."""
  margin_stop: NotRequired[int]
  """Stop-out/liquidation margin level."""
  ordermin: NotRequired[str]
  """Minimum order size (in terms of base currency)."""
  costmin: NotRequired[str]
  """Minimum order cost (in terms of quote currency)."""
  tick_size: NotRequired[str]
  """Minimum increment between valid price levels."""
  status: NotRequired[
    Literal['online', 'cancel_only', 'post_only', 'limit_only', 'reduce_only']
  ]
  """Status of the pair."""
  long_position_limit: NotRequired[int]
  """Maximum long margin position size (in terms of base currency)."""
  short_position_limit: NotRequired[int]
  """Maximum short margin position size (in terms of base currency)."""


validate_asset_pairs = validator(dict[str, AssetPair])


class AssetPairs(RpcEndpoint):
  """`spot.market_data.asset_pairs`."""

  async def asset_pairs(
    self,
    *,
    asset_version: Literal[1] | None = None,
    pair: str | None = None,
    aclass_base: Literal['currency', 'tokenized_asset'] | None = None,
    info: Literal['info', 'leverage', 'fees', 'margin'] | None = None,
    country_code: str | None = None,
    execution_venue: Literal['international', 'bitnomial_exchange'] | None = None,
  ) -> dict[str, AssetPair]:
    """Get tradable asset pairs.

    Args:
      asset_version: Controls whether response keys and asset identifier fields use Kraken's internal names or display names. Omitted (default): internal names are used, pair keys use the internal format (`XXBTZUSD`), and `base`/`quote`/`fee_volume_currency` use internal names. `assetVersion=1`: display names are used, pair keys become the slash-separated display format (`BTC/USD`), and `base`/`quote`/`fee_volume_currency` also switch to display names. Only `assetVersion=1` is currently supported. The `altname`/`wsname` fields are not affected by this parameter.
      pair: Asset pairs to get data for (optional, default all tradeable pairs).
      aclass_base: Filters the asset class to retrieve: `currency` (spot currency pairs) or `tokenized_asset` (tokenized asset pairs, i.e. xstocks).
      info: Info to retrieve: `info` (all info), `leverage` (leverage info), `fees` (fee schedule), or `margin` (margin info).
      country_code: Filter for response to only include pairs available in the provided country/region (ISO 3166-1 alpha-2 code).
      execution_venue: Filter by execution venue: `international` (International exchange) or `bitnomial_exchange` (Bitnomial exchange).

    References:
      - [Official docs](https://docs.kraken.com/api-reference/market-data/get-tradable-asset-pairs)
    """
    params = {}
    if asset_version is not None:
      params['assetVersion'] = asset_version
    if pair is not None:
      params['pair'] = pair
    if aclass_base is not None:
      params['aclass_base'] = aclass_base
    if info is not None:
      params['info'] = info
    if country_code is not None:
      params['country_code'] = country_code
    if execution_venue is not None:
      params['execution_venue'] = execution_venue

    return await self.request(
      '/0/public/AssetPairs', params, validator=validate_asset_pairs
    )
