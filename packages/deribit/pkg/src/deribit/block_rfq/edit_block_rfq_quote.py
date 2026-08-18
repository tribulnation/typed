"""`private/edit_block_rfq_quote` — `private/edit_block_rfq_quote`."""

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


class EditBlockRfqQuoteLeg(TypedDict):
  """One leg's revised price/ratio/direction for this quote."""

  instrument_name: str
  """Unique instrument identifier."""
  price: float
  """Price for this leg."""
  ratio: int
  """Ratio of amount between legs."""
  direction: Literal['buy', 'sell']
  """Direction: `buy`, or `sell`."""


class BlockRfqQuote(TypedDict):
  """The quote after editing, with `replaced: true`."""

  creation_timestamp: int
  """When the quote was originally created (ms since epoch)."""
  last_update_timestamp: NotRequired[int]
  """When the quote was last updated (ms since epoch) -- this edit."""
  block_rfq_id: int
  """ID of the Block RFQ."""
  block_rfq_quote_id: int
  """ID of the edited quote."""
  quote_state: str
  """State of the quote. No documented enumerated set of values -- left bare per docs/spec/authoring.md rule 2."""
  execution_instruction: NotRequired[Literal['any_part_of', 'all_or_none']]
  """Execution instruction of the quote, echoing the request or its default."""
  price: float
  """Price of the quote."""
  amount: float
  """This value multiplied by the ratio of a leg gives trade size on that leg."""
  direction: Literal['buy', 'sell']
  """Direction of trade from the maker's perspective."""
  filled_amount: NotRequired[float]
  """Filled amount of the quote."""
  legs: list[BlockRfqQuoteLeg]
  """The revised instrument legs this quote covers."""
  hedge: NotRequired[BlockRfqQuoteHedge]
  replaced: bool
  """Always `true` in the response to a successful edit."""
  label: NotRequired[str]
  """User defined label for the quote."""
  app_name: NotRequired[str]
  """The application that placed the quote on behalf of the user."""
  quote_state_reason: NotRequired[str]
  """Reason for quote cancellation, present when the edit resulted in cancellation."""


validate_edit_block_rfq_quote = validator[BlockRfqQuote](BlockRfqQuote)


class EditBlockRfqQuote(RpcEndpoint):
  """`private/edit_block_rfq_quote`."""

  async def edit_block_rfq_quote(
    self,
    *,
    legs: list[EditBlockRfqQuoteLeg],
    amount: float,
    direction: Literal['buy', 'sell'],
    block_rfq_quote_id: int | None = None,
    label: str | None = None,
    hedge: str | None = None,
    block_rfq_id: int | None = None,
    execution_instruction: Literal['all_or_none', 'any_part_of'] | None = None,
    price: float | None = None,
    validate: bool | None = None,
  ) -> BlockRfqQuote:
    """**Maker method**

    Edits a Block RFQ quote identified by `block_rfq_quote_id`, or by `block_rfq_id`+`label`.

    Scope: `block_rfq:read_write`.

    Args:
      legs: List of legs used for the revised Block RFQ quote.
      amount: This value multiplied by the ratio of a leg gives trade size on that leg.
      direction: Direction of trade from the maker's perspective. Not listed in the venue's own OpenAPI `parameters` array, but present in its documented request example -- see upstream.md.
      block_rfq_quote_id: Identifies the quote to edit (alternative to `block_rfq_id`+`label`).
      label: Used together with `block_rfq_id` to identify the quote to edit.
      hedge: Hedge leg of the Block RFQ, as a JSON-encoded string.
      block_rfq_id: Used together with `label` to identify the quote to edit.
      execution_instruction: Execution instruction of the quote. Not listed in the venue's own OpenAPI `parameters` array, but present in its documented request example -- see upstream.md.
      price: Aggregated price used for quoting future spreads.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/block-rfq/private-edit_block_rfq_quote)
    """
    params: dict = {
      'legs': legs,
      'amount': amount,
      'direction': direction,
    }
    if block_rfq_quote_id is not None:
      params['block_rfq_quote_id'] = block_rfq_quote_id
    if label is not None:
      params['label'] = label
    if hedge is not None:
      params['hedge'] = hedge
    if block_rfq_id is not None:
      params['block_rfq_id'] = block_rfq_id
    if execution_instruction is not None:
      params['execution_instruction'] = execution_instruction
    if price is not None:
      params['price'] = price
    return await self.authed_request(
      'private/edit_block_rfq_quote',
      params=params,
      validator=validate_edit_block_rfq_quote,
      validate=validate,
    )
