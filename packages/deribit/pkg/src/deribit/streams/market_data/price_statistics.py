"""`deribit_price_statistics.{index_name}` — subscription."""

from typing_extensions import Any, Literal, NotRequired, TypedDict
from deribit.core import StreamEndpoint
from typed_core.util import StreamManager
from typed_core.validation import validator


class PriceStatisticsUpdate(TypedDict):
  """Basic 24h statistics for a Deribit index."""

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
  ]
  """Index identifier, matching a (base) cryptocurrency to a quote currency."""
  low24h: float
  """The lowest recorded price within the last 24 hours."""
  high24h: float
  """The highest recorded price within the last 24 hours."""
  change24h: float
  """The price index change between the first and last point within the most recent 24-hour window."""
  fast_market: NotRequired[bool]
  """Whether the index is in a fast-moving-prices period: `true` when the price index value drastically changed within the last hour, remaining `true` for 2 more hours after prices calm down."""


validate_price_statistics = validator[PriceStatisticsUpdate](PriceStatisticsUpdate)


class PriceStatistics(StreamEndpoint):
  """`deribit_price_statistics.{index_name}` subscription."""

  def price_statistics(
    self,
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
    *,
    validate: bool | None = None,
  ) -> StreamManager[PriceStatisticsUpdate, Any, Any]:
    """Basic statistics for the Deribit index identified by `index_name` -- aggregated stats derived from index updates, useful for monitoring index behavior over time.

    Args:
      index_name: Index identifier, matching a (base) cryptocurrency to a quote currency.
      validate: Validate pushed payloads against the expected schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/subscriptions/market-data/deribit_price_statisticsindex_name)
    """
    channel = f'deribit_price_statistics.{index_name}'
    return self.subscribe(
      channel, validator=validate_price_statistics, validate=validate
    )
