"""`private/cancel_block_rfq` — `private/cancel_block_rfq`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class BlockRfqLeg(TypedDict):
  """One leg of a (possibly multi-leg) Block RFQ."""

  ratio: int
  """Ratio of amount between legs."""
  instrument_name: str
  """Unique instrument identifier."""
  direction: Literal['buy', 'sell']
  """Direction: `buy`, or `sell`."""


class BlockRfqQuoteSummaryAsksItem(TypedDict):
  """One side (bid or ask) of the current Block RFQ order book."""

  makers: NotRequired[list[str]]
  """Aliases of the makers backing this quote level."""
  price: NotRequired[float]
  """Price of a quote."""
  last_update_timestamp: NotRequired[int]
  """When this quote was last updated (ms since epoch)."""
  execution_instruction: NotRequired[Literal['any_part_of', 'all_or_none']]
  """Execution instruction of the quote. Default `any_part_of`."""
  amount: NotRequired[float]
  """This value multiplied by the ratio of a leg gives trade size on that leg."""
  expires_at: NotRequired[int]
  """When the quote expires (ms since epoch)."""


class BlockRfqQuoteSummaryBidsItem(TypedDict):
  """One side (bid or ask) of the current Block RFQ order book."""

  makers: NotRequired[list[str]]
  """Aliases of the makers backing this quote level."""
  price: NotRequired[float]
  """Price of a quote."""
  last_update_timestamp: NotRequired[int]
  """When this quote was last updated (ms since epoch)."""
  execution_instruction: NotRequired[Literal['any_part_of', 'all_or_none']]
  """Execution instruction of the quote. Default `any_part_of`."""
  amount: NotRequired[float]
  """This value multiplied by the ratio of a leg gives trade size on that leg."""
  expires_at: NotRequired[int]
  """When the quote expires (ms since epoch)."""


class BlockRfq(TypedDict):
  """The Block RFQ, now in `cancelled` state."""

  creation_timestamp: int
  """When the Block RFQ was created (ms since epoch)."""
  expiration_timestamp: NotRequired[int]
  """When the Block RFQ would have expired (ms since epoch)."""
  timestamp: NotRequired[int]
  """Cancellation timestamp (ms since epoch) -- observed live, not in the venue's own OpenAPI schema."""
  block_rfq_id: int
  """ID of the Block RFQ."""
  role: Literal['taker', 'maker']
  """Role of the user in this Block RFQ."""
  state: Literal['cancelled']
  """State of the Block RFQ, always `cancelled` in this response."""
  makers: NotRequired[list[str]]
  """Targeted Block RFQ makers."""
  amount: float
  """This value multiplied by the ratio of a leg gives trade size on that leg."""
  min_trade_amount: NotRequired[float]
  """Minimum amount for trading."""
  asks: NotRequired[list[BlockRfqQuoteSummaryAsksItem]]
  """Open ask quotes on this Block RFQ at cancellation time."""
  bids: NotRequired[list[BlockRfqQuoteSummaryBidsItem]]
  """Open bid quotes on this Block RFQ at cancellation time."""
  legs: list[BlockRfqLeg]
  """The instrument legs making up this Block RFQ."""
  combo_id: NotRequired[str]
  """Unique combo identifier (equals the sole leg's `instrument_name` for a single-leg RFQ)."""
  label: NotRequired[str]
  """User defined label for the Block RFQ."""
  disclosed: NotRequired[bool]
  """Whether the RFQ was created non-anonymous."""
  index_prices: NotRequired[dict[str, float]]
  """A map of index prices for the underlying instrument(s), keyed by price index name, observed at cancellation time."""
  included_in_taker_rating: NotRequired[bool]
  """Whether the RFQ counts toward the taker's rating."""


validate_cancel_block_rfq = validator[BlockRfq](BlockRfq)


class CancelBlockRfq(RpcEndpoint):
  """`private/cancel_block_rfq`."""

  async def cancel_block_rfq(
    self,
    *,
    block_rfq_id: int,
    validate: bool | None = None,
  ) -> BlockRfq:
    """**Taker method**

    Cancels a Block RFQ using the specified `block_rfq_id`.

    Scope: `block_rfq:read_write`.

    Args:
      block_rfq_id: ID of the Block RFQ to cancel.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/block-rfq/private-cancel_block_rfq)
    """
    params: dict = {
      'block_rfq_id': block_rfq_id,
    }
    return await self.authed_request(
      'private/cancel_block_rfq',
      params=params,
      validator=validate_cancel_block_rfq,
      validate=validate,
    )
