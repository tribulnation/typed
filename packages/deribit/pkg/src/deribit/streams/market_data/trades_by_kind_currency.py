"""`trades.{kind}.{currency}.{interval}` — subscription."""

from typing_extensions import Any, Literal, NotRequired, TypedDict
from deribit.core import StreamEndpoint
from typed_core.util import StreamManager
from typed_core.validation import validator


class TradeUpdate(TypedDict):
  """One executed trade."""

  trade_id: str
  """Unique (per currency) trade identifier."""
  trade_seq: int
  """The sequence number of the trade within the instrument."""
  instrument_name: str
  """Unique instrument identifier."""
  timestamp: int
  """The timestamp of the trade (milliseconds since the Unix epoch)."""
  starbase_timestamp: NotRequired[int]
  """The Starbase causal timestamp of the trade (nanoseconds since the Unix epoch)."""
  direction: Literal['buy', 'sell']
  """Trade direction."""
  tick_direction: Literal[0, 1, 2, 3]
  """Direction of the "tick": `0` plus tick, `1` zero-plus tick, `2` minus tick, `3` zero-minus tick."""
  index_price: float
  """Index price at the moment of the trade."""
  price: float
  """Price, in base currency."""
  amount: float
  """Trade amount. For perpetual and inverse futures the amount is in USD units; for options and linear futures it is the underlying base currency coin."""
  contracts: NotRequired[float]
  """Trade size in contract units. May be absent for historical trades."""
  iv: NotRequired[float]
  """Option implied volatility for the price (options only)."""
  liquidation: NotRequired[Literal['M', 'T', 'MT']]
  """Present only for trades caused by liquidation: `M` when the maker side was under liquidation, `T` when the taker side was, `MT` when both were."""
  mark_price: float
  """Mark price at the moment of the trade."""
  block_trade_id: NotRequired[str]
  """Block trade id, when the trade was part of a block trade."""
  block_trade_leg_count: NotRequired[int]
  """Block trade leg count, when the trade was part of a block trade."""
  combo_id: NotRequired[str]
  """Combo instrument name, if the trade is a combo trade."""
  combo_trade_id: NotRequired[str]
  """Combo trade identifier, if the trade is a combo trade."""
  starbase_match_id: NotRequired[int]
  """The Starbase match identifier, present only for trades matched via Starbase."""
  block_rfq_id: NotRequired[int]
  """ID of the Block RFQ, when the trade was part of a Block RFQ."""


validate_trades_by_kind_currency = validator[list[TradeUpdate]](list[TradeUpdate])


class TradesByKindCurrency(StreamEndpoint):
  """`trades.{kind}.{currency}.{interval}` subscription."""

  def trades_by_kind_currency(
    self,
    kind: Literal['future', 'option', 'spot', 'future_combo', 'option_combo'],
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR', 'any'],
    interval: Literal['raw', '100ms', 'agg2'],
    *,
    validate: bool | None = None,
  ) -> StreamManager[list[TradeUpdate], Any, Any]:
    """A consolidated stream of trades across all instruments of a given `kind` (e.g. futures, options) and `currency`. `interval` controls aggregation frequency.

    Args:
      kind: Instrument kind.
      currency: Currency code, or `any` for all.
      interval: Frequency of notifications; events are aggregated over this interval. `raw` means no aggregation and is only available to authorized users.
      validate: Validate pushed payloads against the expected schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/subscriptions/trades/tradeskindcurrencyinterval)
    """
    channel = f'trades.{kind}.{currency}.{interval}'
    return self.subscribe(
      channel, validator=validate_trades_by_kind_currency, validate=validate
    )
