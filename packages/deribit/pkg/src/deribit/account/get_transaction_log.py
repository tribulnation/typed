"""`private/get_transaction_log` — `private/get_transaction_log`."""

from typing_extensions import Any, AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class TransactionLogEntry(TypedDict):
  id: int
  """Unique identifier."""
  currency: str
  """Currency of the transaction."""
  timestamp: int
  """The timestamp (milliseconds since the Unix epoch)."""
  user_id: int
  """Unique user identifier."""
  username: NotRequired[str]
  """System name or user-defined subaccount alias."""
  commission: NotRequired[float | None]
  """Commission paid so far, in base currency."""
  cashflow: NotRequired[float]
  """For futures/perpetuals: realized session PNL since last settlement. For options: amount paid or received for the trade."""
  balance: NotRequired[float]
  """Cash balance after the transaction."""
  change: float
  """Change in cash balance -- fees and options premium for trades; futures session PNL and perpetual session funding for settlements."""
  user_seq: int
  """Sequential identifier of the user transaction."""
  type: str
  """Transaction category, e.g. `trade`, `deposit`, `withdrawal`, `settlement`, `delivery`, `transfer`, `swap`, `correction`, `expiry`. Not declared `enum`: the venue documents this list as the "most common" values and says new types can be added at any time."""
  info: NotRequired[dict[str, Any] | str]
  """Additional information about the transaction; shape depends on `type`. Observed live as a plain string (e.g. `"Source: web"`) for trades, and an object for transfers/settlements."""
  equity: NotRequired[float]
  """Updated equity value after the transaction."""
  mark_price: NotRequired[float]
  """Mark price during the trade."""
  settlement_price: NotRequired[float]
  """Settlement price for the instrument during delivery."""
  index_price: NotRequired[float]
  """Index price for the instrument during delivery."""
  instrument_name: NotRequired[str | None]
  """Unique instrument identifier, when the entry relates to one."""
  position: NotRequired[float | None]
  """Updated position size after the transaction."""
  side: NotRequired[str]
  """One of `short`/`long` for settlements, `close sell`/`close buy` for deliveries, `open sell`/`open buy`/`close sell`/`close buy` for trades, or `-` when not applicable. Not declared `enum`: the venue states this list in prose as the shape per entry `type`, not as one closed set for the field overall, and does not rule out further values on `type`s beyond the ones it enumerates."""
  amount: NotRequired[float]
  """Requested order size (USD for perpetual/inverse futures, base currency coin for options/linear futures)."""
  price: NotRequired[float | None]
  """Settlement/delivery price, or the price level of the traded contracts."""
  price_currency: NotRequired[str]
  """Currency symbol the `price` field is denominated in."""
  trade_id: NotRequired[str | None]
  """Unique (per-currency) trade identifier, when the entry relates to a trade."""
  order_id: NotRequired[str | None]
  """Unique order identifier, when the entry relates to an order."""
  user_role: NotRequired[Literal['maker', 'taker']]
  """The user's trade role."""
  fee_role: NotRequired[Literal['maker', 'taker']]
  """The user's fee role -- can differ from `user_role` when an iceberg order was involved in matching."""
  profit_as_cashflow: NotRequired[bool]
  """Whether the cashflow is waiting for settlement."""
  interest_pl: NotRequired[float]
  """Actual funding rate of trades/settlements on perpetual instruments."""
  block_rfq_id: NotRequired[int]
  """Id of the Block RFQ, when the trade was part of one."""
  ip: NotRequired[str]
  """IP address the trade was initiated from."""
  contracts: NotRequired[float]
  """Order size in contract units (optional, may be absent in historical data)."""


class GetTransactionLogResult(TypedDict):
  continuation: int | None
  """Continuation token for the next page; `null` when there is no further page."""
  logs: list[TransactionLogEntry]
  """Transaction log entries for this page, newest first."""


validate_get_transaction_log = validator[GetTransactionLogResult](
  GetTransactionLogResult
)


class GetTransactionLog(RpcEndpoint):
  """`private/get_transaction_log`."""

  async def get_transaction_log(
    self,
    *,
    currency: Literal[
      'BTC',
      'ETH',
      'STETH',
      'ETHW',
      'USDC',
      'USDT',
      'EURR',
      'SOL',
      'XRP',
      'USYC',
      'PAXG',
      'BNB',
      'USDE',
    ],
    start_timestamp: int,
    end_timestamp: int,
    query: str | None = None,
    count: int | None = None,
    subaccount_id: int | None = None,
    continuation: int | None = None,
    validate: bool | None = None,
  ) -> GetTransactionLogResult:
    """Retrieves a detailed transaction log for the authenticated account: trades, deposits, withdrawals, transfers, fees, and other balance-affecting operations, filterable by currency, time range and keyword. No time limit -- history is queryable back to account creation. Rate limited to 1 request/second. Paginated via the `continuation` cursor.

    Args:
      currency: The currency symbol.
      start_timestamp: The earliest timestamp to return results from (milliseconds since the Unix epoch).
      end_timestamp: The most recent timestamp to return results from (milliseconds since the Unix epoch).
      query: Filter keyword, e.g. `trade`, `maker`, `taker`, `open`, `close`, `liquidation`, `buy`, `sell`, `withdrawal`, `delivery`, `settlement`, `deposit`, `transfer`, `option`, `future`, `correction`, `block_trade`, `swap`, `expiry`, or a withdrawal/transfer address.
      count: Count of transaction log entries to return, default 100, maximum 250.
      subaccount_id: Id of a subaccount.
      continuation: Continuation token from a previous response, to fetch the next page.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/account-management/private-get_transaction_log)
    """
    params: dict = {
      'currency': currency,
      'start_timestamp': start_timestamp,
      'end_timestamp': end_timestamp,
    }
    if query is not None:
      params['query'] = query
    if count is not None:
      params['count'] = count
    if subaccount_id is not None:
      params['subaccount_id'] = subaccount_id
    if continuation is not None:
      params['continuation'] = continuation
    return await self.authed_request(
      'private/get_transaction_log',
      params=params,
      validator=validate_get_transaction_log,
      validate=validate,
    )

  async def get_transaction_log_paged(
    self,
    *,
    currency: Literal[
      'BTC',
      'ETH',
      'STETH',
      'ETHW',
      'USDC',
      'USDT',
      'EURR',
      'SOL',
      'XRP',
      'USYC',
      'PAXG',
      'BNB',
      'USDE',
    ],
    start_timestamp: int,
    end_timestamp: int,
    query: str | None = None,
    count: int | None = None,
    subaccount_id: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[GetTransactionLogResult]:
    """Yield successive pages of `get_transaction_log`.

    Passes each page's token back as `continuation` and stops when a response carries no
    `continuation`, or after `max_pages` pages when one is given.
    """
    continuation: int | None = None
    pages = 0
    while True:
      response = await self.get_transaction_log(
        currency=currency,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        query=query,
        count=count,
        subaccount_id=subaccount_id,
        continuation=continuation,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      continuation = response.get('continuation') if response is not None else None
      if not continuation:
        break
