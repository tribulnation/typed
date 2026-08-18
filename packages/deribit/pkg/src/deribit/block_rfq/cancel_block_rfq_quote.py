"""`private/cancel_block_rfq_quote` — `private/cancel_block_rfq_quote`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class BlockRfqQuoteHedge(TypedDict):
  """The hedge leg of the quote, when one was included."""

  amount: NotRequired[int]
  """The requested hedge leg size."""
  instrument_name: NotRequired[str]
  """Unique instrument identifier."""
  direction: NotRequired[Literal['buy', 'sell']]
  """Direction: `buy`, or `sell`."""
  price: NotRequired[float]
  """Price for the hedge leg."""


class BlockRfqQuoteLeg(TypedDict):
  """One leg of a (possibly multi-leg) Block RFQ quote."""

  ratio: int
  """Ratio of amount between legs."""
  instrument_name: str
  """Unique instrument identifier."""
  direction: Literal['buy', 'sell']
  """Direction: `buy`, or `sell`."""
  price: float
  """Price for this leg."""


class BlockRfqQuote(TypedDict):
  """The quote, now cancelled."""

  creation_timestamp: int
  """When the quote was created (ms since epoch)."""
  last_update_timestamp: NotRequired[int]
  """When the quote was last updated (ms since epoch) -- this cancellation."""
  block_rfq_id: int
  """ID of the Block RFQ."""
  block_rfq_quote_id: int
  """ID of the cancelled quote."""
  quote_state: str
  """State of the quote, reflecting cancellation. No documented enumerated set of values -- left bare per docs/spec/authoring.md rule 2."""
  execution_instruction: NotRequired[Literal['any_part_of', 'all_or_none']]
  """Execution instruction the quote was placed with."""
  price: float
  """Price of the quote."""
  amount: float
  """This value multiplied by the ratio of a leg gives trade size on that leg."""
  direction: Literal['buy', 'sell']
  """Direction of trade from the maker's perspective."""
  filled_amount: NotRequired[float]
  """Filled amount of the quote at the time of cancellation."""
  legs: list[BlockRfqQuoteLeg]
  """The instrument legs this quote covered."""
  hedge: NotRequired[BlockRfqQuoteHedge]
  replaced: NotRequired[bool]
  """Whether the quote had been edited before cancellation."""
  label: NotRequired[str]
  """User defined label for the quote."""
  app_name: NotRequired[str]
  """The application that placed the quote on behalf of the user."""
  quote_state_reason: NotRequired[str]
  """Reason for the cancellation."""


validate_cancel_block_rfq_quote = validator[BlockRfqQuote](BlockRfqQuote)


class CancelBlockRfqQuote(RpcEndpoint):
  """`private/cancel_block_rfq_quote`."""

  async def cancel_block_rfq_quote(
    self,
    *,
    block_rfq_quote_id: int | None = None,
    label: str | None = None,
    block_rfq_id: int | None = None,
    validate: bool | None = None,
  ) -> BlockRfqQuote:
    """**Maker method**

    Cancels a single Block RFQ quote, identified by `block_rfq_quote_id` or by `block_rfq_id`+`label`. Mass cancellation by label is not supported -- this cancels only one quote; use `private/cancel_all_block_rfq_quotes` to cancel all of them.

    Scope: `block_rfq:read_write`.

    Args:
      block_rfq_quote_id: Identifies the quote to cancel (alternative to `block_rfq_id`+`label`).
      label: Used together with `block_rfq_id` to identify the quote to cancel.
      block_rfq_id: Used together with `label` to identify the quote to cancel.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/block-rfq/private-cancel_block_rfq_quote)
    """
    params = {}
    if block_rfq_quote_id is not None:
      params['block_rfq_quote_id'] = block_rfq_quote_id
    if label is not None:
      params['label'] = label
    if block_rfq_id is not None:
      params['block_rfq_id'] = block_rfq_id
    return await self.authed_request(
      'private/cancel_block_rfq_quote',
      params=params,
      validator=validate_cancel_block_rfq_quote,
      validate=validate,
    )
