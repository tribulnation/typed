"""`GET /api/v1/hf/accounts/ledgers` — Get Account Ledgers - Trade_hf."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class TradeHfLedgerEntryRow(TypedDict):
  id: str
  """Unique ledger entry ID, decreasing with age -- feed the last row's `id` back as the next call's `lastId` to page further back."""
  currency: str
  """Currency."""
  amount: str
  """Change in funds balance."""
  fee: str
  """Fee charged, if any."""
  tax: str
  """Tax withheld, if any."""
  balance: str
  """Account balance after this entry."""
  accountType: Literal['TRADE_HF']
  """Always `TRADE_HF` for this endpoint."""
  bizType: Literal[
    'TRADE_EXCHANGE',
    'TRANSFER',
    'SUB_TRANSFER',
    'RETURNED_FEES',
    'DEDUCTION_FEES',
    'OTHER',
  ]
  """Business type causing this entry."""
  direction: Literal['in', 'out']
  """Fund flow direction."""
  createdAt: str
  """Unix milliseconds this entry occurred, as a decimal string."""
  context: str
  """JSON-encoded business context; for `TRADE_EXCHANGE` this is `{symbol, orderId, tradeId}`, `{}` otherwise."""


_Type = list[TradeHfLedgerEntryRow]
adapter = validator[_Type](_Type)  # type: ignore


class HfLedgers(RpcEndpoint):
  """`Get Account Ledgers - Trade_hf` — mixed into `Account`, the product exposing `account.hf_ledgers`."""

  async def hf_ledgers(
    self,
    *,
    currency: str | None = None,
    direction: Literal['in', 'out'] | None = None,
    biz_type: Literal[
      'TRADE_EXCHANGE',
      'TRANSFER',
      'SUB_TRANSFER',
      'RETURNED_FEES',
      'DEDUCTION_FEES',
      'OTHER',
    ]
    | None = None,
    last_id: int | None = None,
    limit: int | None = None,
    start_at: int | None = None,
    end_at: int | None = None,
    validate: bool | None = None,
  ) -> list[TradeHfLedgerEntryRow]:
    """List transfer (in/out) records for the high-frequency trading account, newest first by `createdAt` then `id`, restricted to the last 7 days.

    Args:
      currency: Currency, or up to 10 comma-separated currencies. Queries all currencies if omitted.
      direction: Fund flow direction.
      biz_type: Business type causing the ledger entry.
      last_id: The `id` of the last entry from the previous page; returns entries older than it. Omit for the most recent page.
      limit: Results per page.
      start_at: Start time, Unix milliseconds.
      end_at: End time, Unix milliseconds.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if currency is not None:
      params['currency'] = currency
    if direction is not None:
      params['direction'] = direction
    if biz_type is not None:
      params['bizType'] = biz_type
    if last_id is not None:
      params['lastId'] = last_id
    if limit is not None:
      params['limit'] = limit
    if start_at is not None:
      params['startAt'] = start_at
    if end_at is not None:
      params['endAt'] = end_at
    return await self.authed_request(
      'GET',
      '/api/v1/hf/accounts/ledgers',
      params=params,
      validator=adapter,
      validate=validate,
    )
