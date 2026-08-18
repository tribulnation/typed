"""`markprice.options.{index_name}` — subscription."""

from typing_extensions import Any, Literal, NotRequired, TypedDict
from deribit.core import StreamEndpoint
from typed_core.util import StreamManager
from typed_core.validation import validator


class OptionMarkPrice(TypedDict):
  """One option's mark price update."""

  instrument_name: NotRequired[str]
  """Unique instrument identifier."""
  mark_price: NotRequired[float]
  """The mark price for the instrument."""
  iv: NotRequired[float]
  """Implied volatility of the underlying instrument."""
  timestamp: NotRequired[int]
  """The timestamp (milliseconds since the Unix epoch)."""


validate_mark_price_options = validator[list[OptionMarkPrice]](list[OptionMarkPrice])


class MarkPriceOptions(StreamEndpoint):
  """`markprice.options.{index_name}` subscription."""

  def mark_price_options(
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
  ) -> StreamManager[list[OptionMarkPrice], Any, Any]:
    """Options mark price updates for the given `index_name` -- mark prices for every option under the index, useful for valuation, risk monitoring, and P&L calculations.

    Args:
      index_name: Index identifier, matching a (base) cryptocurrency to a quote currency.
      validate: Validate pushed payloads against the expected schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/subscriptions/market-data/markpriceoptionsindex_name)
    """
    channel = f'markprice.options.{index_name}'
    return self.subscribe(
      channel, validator=validate_mark_price_options, validate=validate
    )
