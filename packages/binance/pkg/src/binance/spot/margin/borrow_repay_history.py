from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MarginBorrowRepayRecord(TypedDict):
  """A single borrow/repay record."""

  isolatedSymbol: NotRequired[str]
  """Isolated symbol; not returned for crossed margin."""
  amount: NotRequired[str]
  """Total amount borrowed or repaid."""
  asset: str
  """Asset borrowed or repaid."""
  interest: NotRequired[str]
  """Interest repaid, when repaying."""
  principal: str
  """Principal borrowed or repaid."""
  status: Literal['PENDING', 'CONFIRMED', 'FAILED']
  """Execution status of the record."""
  timestamp: int
  """Millisecond epoch time of the record."""
  txId: int
  """Transaction id of the borrow/repay operation."""


class MarginBorrowRepayHistoryPage(TypedDict):
  """One page of margin borrow/repay records."""

  rows: list[MarginBorrowRepayRecord]
  """Borrow/repay records for this page."""
  total: int
  """Total number of records matching the query."""


class BorrowRepayHistory(RpcEndpoint):
  """Query borrow/repay records in margin account"""

  async def borrow_repay_history(
    self,
    *,
    asset: str,
    isolated_symbol: str | None = None,
    tx_id: int | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    current: int | None = None,
    size: int | None = None,
    type: Literal['BORROW', 'REPAY'],
    validate: bool | None = None,
  ) -> MarginBorrowRepayHistoryPage:
    """Query this account's margin borrow/repay records, in descending order. `txId` or `startTime` must be sent; `txId` takes precedence. If `asset` is sent, up to 30 days of data before `endTime` is returned; if not, up to 7 days. If neither `startTime` nor `endTime` is sent, the recent 7 days are returned; `startTime` defaults to `endTime` minus 7 days, `endTime` defaults to now.

    Args:
      asset: Asset to query.
      isolated_symbol: Isolated margin symbol. Omit for crossed margin.
      tx_id: Transaction id (`tranId` returned by `POST /sapi/v1/margin/borrow-repay`) to look up directly. Takes precedence over `startTime` when both are sent.
      start_time: Millisecond epoch start of the queried window. Defaults to `endTime` minus 7 days.
      end_time: Millisecond epoch end of the queried window. Defaults to the current time.
      current: Page number, starting from 1.
      size: Page size.
      type: Whether to query borrow or repay records.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/borrow-repay#query-borrow-repay-records-in-margin-account)
    """
    params: dict = {
      'asset': asset,
      'type': type,
    }
    if isolated_symbol is not None:
      params['isolatedSymbol'] = isolated_symbol
    if tx_id is not None:
      params['txId'] = tx_id
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    _Response = MarginBorrowRepayHistoryPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/margin/borrow-repay',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def borrow_repay_history_paged(
    self,
    *,
    asset: str,
    isolated_symbol: str | None = None,
    tx_id: int | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    size: int | None = None,
    type: Literal['BORROW', 'REPAY'],
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[MarginBorrowRepayHistoryPage]:
    """Yield successive pages of `borrow_repay_history`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.borrow_repay_history(
        asset=asset,
        isolated_symbol=isolated_symbol,
        tx_id=tx_id,
        start_time=start_time,
        end_time=end_time,
        size=size,
        type=type,
        current=current,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or size is None or pages * size >= total:
        break
      current += 1
