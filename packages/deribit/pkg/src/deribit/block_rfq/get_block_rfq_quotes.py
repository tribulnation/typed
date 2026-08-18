"""`private/get_block_rfq_quotes` — `private/get_block_rfq_quotes`."""

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
  """One quote placed by the (maker) caller against a Block RFQ."""

  creation_timestamp: int
  """When the quote was created (ms since epoch)."""
  last_update_timestamp: NotRequired[int]
  """When the quote was last updated (ms since epoch)."""
  block_rfq_id: int
  """ID of the Block RFQ."""
  block_rfq_quote_id: int
  """ID of the Block RFQ quote."""
  quote_state: str
  """State of the quote. The venue documents this field with no enumerated set of values, so it is left as a bare string rather than a guessed closed set (docs/spec/authoring.md rule 2)."""
  execution_instruction: NotRequired[Literal['any_part_of', 'all_or_none']]
  """Execution instruction of the quote. Default `any_part_of`. `all_or_none` fills entirely or not at all and has priority over `any_part_of` at the same price level; `any_part_of` may fill partially."""
  price: float
  """Price of the quote."""
  amount: float
  """This value multiplied by the ratio of a leg gives trade size on that leg."""
  direction: Literal['buy', 'sell']
  """Direction of trade from the maker's perspective."""
  filled_amount: NotRequired[float]
  """Filled amount of the quote. USD units for perpetual/futures, underlying cryptocurrency units for options."""
  legs: list[BlockRfqQuoteLeg]
  """The instrument legs this quote covers."""
  hedge: NotRequired[BlockRfqQuoteHedge]
  replaced: NotRequired[bool]
  """Whether the quote was edited (via `private/edit_block_rfq_quote`)."""
  label: NotRequired[str]
  """User defined label for the quote (maximum 64 characters)."""
  app_name: NotRequired[str]
  """The application that placed the quote on behalf of the user."""
  quote_state_reason: NotRequired[str]
  """Reason for quote cancellation, present when the quote was cancelled."""


validate_get_block_rfq_quotes = validator[list[BlockRfqQuote]](list[BlockRfqQuote])


class GetBlockRfqQuotes(RpcEndpoint):
  """`private/get_block_rfq_quotes`."""

  async def get_block_rfq_quotes(
    self,
    *,
    block_rfq_id: int | None = None,
    label: str | None = None,
    block_rfq_quote_id: int | None = None,
    validate: bool | None = None,
  ) -> list[BlockRfqQuote]:
    """**Maker method**

    Retrieves all open quotes for Block RFQs. When `block_rfq_id` is given, only that Block RFQ's open quotes are returned. When `label` is given, all quotes with that label are returned. `block_rfq_quote_id` returns one specific quote.

    Scope: `block_rfq:read`.

    Args:
      block_rfq_id: Scope to open quotes for this Block RFQ.
      label: Return quotes carrying this label.
      block_rfq_quote_id: Return this one specific quote.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/block-rfq/private-get_block_rfq_quotes)
    """
    params = {}
    if block_rfq_id is not None:
      params['block_rfq_id'] = block_rfq_id
    if label is not None:
      params['label'] = label
    if block_rfq_quote_id is not None:
      params['block_rfq_quote_id'] = block_rfq_quote_id
    return await self.authed_request(
      'private/get_block_rfq_quotes',
      params=params,
      validator=validate_get_block_rfq_quotes,
      validate=validate,
    )
