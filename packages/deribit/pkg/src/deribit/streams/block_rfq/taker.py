"""`block_rfq.taker.{currency}` — subscription."""

from typing_extensions import Any, Literal, NotRequired, TypedDict
from deribit.core import StreamEndpoint
from typed_core.util import StreamManager
from typed_core.validation import validator


class BlockRfqClientAllocationInfo(TypedDict):
  """Client allocation info for brokers."""

  client_id: NotRequired[int]
  """ID of a client; available to broker. Represents a group of users under a common name."""
  client_link_id: NotRequired[int]
  """ID assigned to a single user in a client; available to broker."""
  name: NotRequired[str]
  """Name of the linked user within the client; available to broker."""


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


class BlockRfqTakerQuoteAsksItem(TypedDict):
  makers: NotRequired[list[str]]
  """Makers backing this quote."""
  price: NotRequired[float]
  """Price of a quote."""
  last_update_timestamp: NotRequired[int]
  """Timestamp of the last update of the quote (milliseconds since the UNIX epoch)."""
  execution_instruction: NotRequired[Literal['any_part_of', 'all_or_none']]
  """Execution instruction of the quote. Default `any_part_of`.

- `all_or_none` (AON) - the quote can only be filled entirely or not at all, and has priority over `any_part_of` quotes at the same price level.
- `any_part_of` (APO) - the quote can be filled partially or fully."""
  amount: NotRequired[float]
  """This value multiplied by the ratio of a leg gives trade size on that leg."""
  expires_at: NotRequired[int]
  """The timestamp when the quote expires (milliseconds since the Unix epoch), equal to the earliest expiry of placed quotes."""


class BlockRfqTakerQuoteBidsItem(TypedDict):
  makers: NotRequired[list[str]]
  """Makers backing this quote."""
  price: NotRequired[float]
  """Price of a quote."""
  last_update_timestamp: NotRequired[int]
  """Timestamp of the last update of the quote (milliseconds since the UNIX epoch)."""
  execution_instruction: NotRequired[Literal['any_part_of', 'all_or_none']]
  """Execution instruction of the quote. Default `any_part_of`.

- `all_or_none` (AON) - the quote can only be filled entirely or not at all, and has priority over `any_part_of` quotes at the same price level.
- `any_part_of` (APO) - the quote can be filled partially or fully."""
  amount: NotRequired[float]
  """This value multiplied by the ratio of a leg gives trade size on that leg."""
  expires_at: NotRequired[int]
  """The timestamp when the quote expires (milliseconds since the Unix epoch), equal to the earliest expiry of placed quotes."""


class BlockRfqTakerTradeFill(TypedDict):
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


class BlockRfqTradeTrigger(TypedDict):
  """Present only if a trade trigger was placed by the taker; only visible to the taker."""

  state: Literal['triggered', 'untriggered', 'cancelled']
  """Trade trigger state."""
  price: float
  """Price of the trade trigger."""
  direction: Literal['buy', 'sell']
  """Direction of the trade trigger."""
  cancel_reason: NotRequired[str]
  """Reason for cancellation, present only when state is `cancelled`."""


class BlockRfqTradeAllocation(TypedDict):
  user_id: NotRequired[int]
  """User ID to allocate part of the RFQ amount to. For brokers the User ID is obstructed."""
  client_info: NotRequired[BlockRfqClientAllocationInfo]
  amount: NotRequired[float]
  """Amount allocated to this user or client."""


class BlockRfqTakerUpdate(TypedDict):
  """State of a Block RFQ this account created as taker."""

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
  makers: NotRequired[list[str]]
  """Aliases of makers invited to (or participating in) this Block RFQ."""
  amount: NotRequired[float]
  """This value multiplied by the ratio of a leg gives trade size on that leg."""
  min_trade_amount: NotRequired[float]
  """Minimum amount for trading."""
  asks: NotRequired[list[BlockRfqTakerQuoteAsksItem]]
  """Current resting ask quotes on this Block RFQ."""
  bids: NotRequired[list[BlockRfqTakerQuoteBidsItem]]
  """Current resting bid quotes on this Block RFQ."""
  legs: NotRequired[list[BlockRfqLeg]]
  """Multi-leg structure of this Block RFQ."""
  hedge: NotRequired[BlockRfqHedgeLeg]
  combo_id: NotRequired[str]
  """Unique combo identifier."""
  label: NotRequired[str]
  """User defined label for the Block RFQ (maximum 64 characters)."""
  app_name: NotRequired[str]
  """The name of the application that created the Block RFQ on behalf of the user (optional, visible only to taker)."""
  mark_price: NotRequired[float]
  """The mark price for the instrument."""
  disclosed: NotRequired[bool]
  """Indicates whether the RFQ was created as non-anonymous, meaning taker and maker aliases are visible to counterparties."""
  taker: NotRequired[str]
  """Taker alias. Present only when `disclosed` is `true`."""
  index_prices: NotRequired[dict[str, Any]]
  """Index prices for underlying instruments, keyed by index name."""
  included_in_taker_rating: NotRequired[bool]
  """Indicates whether the RFQ is included in the taker's rating calculation. Present only for closed RFQs created by the requesting taker."""
  trades: NotRequired[list[BlockRfqTakerTradeFill]]
  """Fills, once the Block RFQ has been filled."""
  trade_trigger: NotRequired[BlockRfqTradeTrigger]
  trade_allocations: NotRequired[list[BlockRfqTradeAllocation]]
  """Allocations for Block RFQ pre-allocation, splitting the amount between (sub)accounts. Visible only to the taker."""


validate_taker = validator[BlockRfqTakerUpdate](BlockRfqTakerUpdate)


class Taker(StreamEndpoint):
  """`block_rfq.taker.{currency}` subscription."""

  def taker(
    self,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR', 'any'],
    *,
    validate: bool | None = None,
  ) -> StreamManager[BlockRfqTakerUpdate, Any, Any]:
    """Notifications about the state of a Block RFQ this account created as taker. `trades` only appear once the Block RFQ has been filled.

    After a Block RFQ is created, a 5-second grace period begins during which the taker cannot see quotes or trade it.

    Args:
      currency: Currency code or `any` for all

    **Allowed values:** `BTC`, `ETH`, `USDC`, `USDT`, `EURR`, `any`
      validate: Validate pushed payloads against the expected schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/subscriptions/block-rfq/block_rfqtakercurrency)
    """
    channel = f'block_rfq.taker.{currency}'
    return self.authed_subscribe(channel, validator=validate_taker, validate=validate)
