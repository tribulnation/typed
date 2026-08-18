"""`private/create_block_rfq` — `private/create_block_rfq`."""

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


class CreateBlockRfqAllocationClientInfo(TypedDict):
  """Broker client allocation info, when this allocation targets a broker client rather than a direct user id."""

  client_id: NotRequired[int]
  """ID of a client group; available to brokers."""
  client_link_id: NotRequired[int]
  """ID of a single user within a client group; available to brokers."""


class CreateBlockRfqLeg(TypedDict):
  """One leg to include in the new Block RFQ."""

  instrument_name: str
  """Unique instrument identifier."""
  amount: float
  """The requested order size. USD units for perpetual/inverse futures, underlying base currency coin for options/linear futures. Subject to a per-currency minimum notional not documented ahead of time -- see notes."""
  direction: Literal['buy', 'sell']
  """Direction: `buy`, or `sell`."""


class BlockRfq(TypedDict):
  """The created Block RFQ, in its initial `created`/`open` state."""

  creation_timestamp: int
  """When the Block RFQ was created (ms since epoch)."""
  expiration_timestamp: NotRequired[int]
  """When the Block RFQ will expire (ms since epoch)."""
  block_rfq_id: int
  """ID of the Block RFQ."""
  role: Literal['taker']
  """Role of the caller -- always `taker` for a freshly created Block RFQ."""
  state: Literal['created', 'open', 'filled', 'cancelled', 'expired']
  """State of the Block RFQ. `created` observed live immediately after creation (examples/01); `open`/`filled`/`cancelled`/`expired` are the states documented elsewhere in this subdivision."""
  makers: NotRequired[list[str]]
  """Targeted Block RFQ makers."""
  amount: float
  """This value multiplied by the ratio of a leg gives trade size on that leg."""
  min_trade_amount: NotRequired[float]
  """Minimum amount for trading."""
  asks: NotRequired[list[BlockRfqQuoteSummaryAsksItem]]
  """Open ask quotes on this Block RFQ (empty immediately after creation)."""
  bids: NotRequired[list[BlockRfqQuoteSummaryBidsItem]]
  """Open bid quotes on this Block RFQ (empty immediately after creation)."""
  legs: list[BlockRfqLeg]
  """The instrument legs making up this Block RFQ, echoing the request."""
  combo_id: NotRequired[str]
  """Unique combo identifier (equals the sole leg's `instrument_name` for a single-leg RFQ)."""
  label: NotRequired[str]
  """User defined label for the Block RFQ, echoing the request."""
  disclosed: NotRequired[bool]
  """Whether the RFQ was created non-anonymous. Observed `false` live even with no explicit `disclosed`/`makers` given -- see notes."""
  included_in_taker_rating: NotRequired[bool]
  """Whether the RFQ counts toward the taker's rating."""


class CreateBlockRfqAllocation(TypedDict):
  """One allocation of the new Block RFQ's amount."""

  user_id: NotRequired[int]
  """User ID (subaccount or main account) to allocate part of the RFQ amount."""
  client_info: NotRequired[CreateBlockRfqAllocationClientInfo]
  amount: NotRequired[float]
  """Amount allocated to this user or client."""


validate_create_block_rfq = validator[BlockRfq](BlockRfq)


class CreateBlockRfq(RpcEndpoint):
  """`private/create_block_rfq`."""

  async def create_block_rfq(
    self,
    *,
    legs: list[CreateBlockRfqLeg],
    trade_allocations: list[CreateBlockRfqAllocation] | None = None,
    hedge: str | None = None,
    label: str | None = None,
    makers: list[str] | None = None,
    disclosed: bool | None = None,
    validate: bool | None = None,
  ) -> BlockRfq:
    """**Taker method**

    Creates a new Block RFQ, registering a request for quotes -- no capital is committed and nothing trades until `private/accept_block_rfq` is later called against a maker's quote. The taker can pre-allocate the RFQ's amount across (sub)accounts or broker clients via `trade_allocations`.

    Scope: `block_rfq:read_write`.

    Args:
      legs: List of legs used to create the Block RFQ.
      trade_allocations: List of allocations for Block RFQ pre-allocation.
      hedge: Hedge leg of the Block RFQ, as a JSON-encoded string.
      label: User defined label for the Block RFQ.
      makers: List of targeted Block RFQ makers.
      disclosed: Whether the RFQ is non-anonymous.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/block-rfq/private-create_block_rfq)
    """
    params: dict = {
      'legs': legs,
    }
    if trade_allocations is not None:
      params['trade_allocations'] = trade_allocations
    if hedge is not None:
      params['hedge'] = hedge
    if label is not None:
      params['label'] = label
    if makers is not None:
      params['makers'] = makers
    if disclosed is not None:
      params['disclosed'] = disclosed
    return await self.authed_request(
      'private/create_block_rfq',
      params=params,
      validator=validate_create_block_rfq,
      validate=validate,
    )
