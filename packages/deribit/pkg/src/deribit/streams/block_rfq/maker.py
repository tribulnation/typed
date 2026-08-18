"""`block_rfq.maker.{currency}` — subscription."""

from typing_extensions import Any, Literal, NotRequired, TypedDict
from deribit.core import StreamEndpoint
from typed_core.util import StreamManager
from typed_core.validation import validator


class BlockRfqHedgeLeg(TypedDict):
  """Hedge leg of this Block RFQ, if any."""

  amount: NotRequired[int]
  """It represents the requested hedge leg size. For perpetual and inverse futures the amount is in USD units. For options and linear futures it is the underlying base currency coin."""
  instrument_name: NotRequired[str]
  """Unique instrument identifier."""
  direction: NotRequired[Literal['buy', 'sell']]
  """Direction: `buy`, or `sell`."""
  price: NotRequired[float]
  """Price for a hedge leg."""


class BlockRfqLeg(TypedDict):
  ratio: NotRequired[int]
  """Ratio of amount between legs."""
  instrument_name: NotRequired[str]
  """Unique instrument identifier."""
  direction: NotRequired[Literal['buy', 'sell']]
  """Direction: `buy`, or `sell`."""


class BlockRfqMakerTradeFill(TypedDict):
  direction: NotRequired[Literal['buy', 'sell']]
  """Direction: `buy`, or `sell`."""
  price: NotRequired[float]
  """Price in base currency."""
  amount: NotRequired[float]
  """Trade amount. For options, linear futures, linear perpetuals and spots the amount is denominated in the underlying base currency coin. The inverse perpetuals and inverse futures are denominated in USD units."""
  maker: NotRequired[str]
  """Alias of the maker (optional)."""
  hedge_amount: NotRequired[float]
  """Amount of the hedge leg. For linear futures, linear perpetuals and spots the amount is denominated in the underlying base currency coin. The inverse perpetuals and inverse futures are denominated in USD units."""


class BlockRfqMakerUpdate(TypedDict):
  """A Block RFQ available for this maker to quote on, or an update to one it already quoted."""

  creation_timestamp: NotRequired[int]
  """The timestamp when the Block RFQ was created (milliseconds since the Unix epoch)."""
  expiration_timestamp: NotRequired[int]
  """The timestamp when the Block RFQ will expire (milliseconds since the UNIX epoch)."""
  block_rfq_id: NotRequired[int]
  """ID of the Block RFQ."""
  role: NotRequired[Literal['taker', 'maker']]
  """Role of the user in the Block RFQ."""
  state: NotRequired[Literal['open', 'filled', 'cancelled', 'expired']]
  """State of the Block RFQ."""
  taker_rating: NotRequired[str]
  """Rating of the taker."""
  amount: NotRequired[float]
  """This value multiplied by the ratio of a leg gives trade size on that leg."""
  min_trade_amount: NotRequired[float]
  """Minimum amount for trading."""
  legs: NotRequired[list[BlockRfqLeg]]
  """Multi-leg structure of this Block RFQ."""
  hedge: NotRequired[BlockRfqHedgeLeg]
  combo_id: NotRequired[str]
  """Unique combo identifier."""
  disclosed: NotRequired[bool]
  """Indicates whether the RFQ was created as non-anonymous, meaning taker and maker aliases are visible to counterparties."""
  taker: NotRequired[str]
  """Taker alias. Present only when `disclosed` is `true`."""
  index_prices: NotRequired[dict[str, Any]]
  """Index prices for underlying instruments, keyed by index name."""
  included_in_taker_rating: NotRequired[bool]
  """Indicates whether the RFQ is included in the taker's rating calculation. Present only for closed RFQs created by the requesting taker."""
  trades: NotRequired[list[BlockRfqMakerTradeFill]]
  """Fills, once the Block RFQ has been filled."""


validate_maker = validator[BlockRfqMakerUpdate](BlockRfqMakerUpdate)


class Maker(StreamEndpoint):
  """`block_rfq.maker.{currency}` subscription."""

  def maker(
    self,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR', 'any'],
    *,
    validate: bool | None = None,
  ) -> StreamManager[BlockRfqMakerUpdate, Any, Any]:
    """Real-time notifications for Block RFQs available for the subscribed maker to respond to.

    Notifies enrolled Block RFQ makers when a new Block RFQ is created in the given currency (or all currencies, with `any`) that they can potentially quote on. When a Block RFQ this maker quoted is filled, the resulting trades also arrive on `user.trades.{instrument_name}.{interval}` / `user.trades.{kind}.{currency}.{interval}`, carrying `block_rfq_id`, `block_trade_id`, and `block_rfq_quote_id`.

    Requires `block_rfq:read` scope and, separately, Block RFQ maker enrollment for the account -- see `unverified`.

    Args:
      currency: Currency code or `any` for all

    **Allowed values:** `BTC`, `ETH`, `USDC`, `USDT`, `EURR`, `any`
      validate: Validate pushed payloads against the expected schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/subscriptions/block-rfq/block_rfqmakercurrency)
    """
    channel = f'block_rfq.maker.{currency}'
    return self.authed_subscribe(channel, validator=validate_maker, validate=validate)
