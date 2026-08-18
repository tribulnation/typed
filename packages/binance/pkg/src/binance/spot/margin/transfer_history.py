from typing_extensions import AsyncIterator, Literal, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MarginTransfer(TypedDict):
  """One margin transfer."""

  amount: str
  """Transfer amount."""
  asset: str
  """Asset transferred."""
  status: str
  """Transfer status."""
  timestamp: int
  """Millisecond epoch transfer timestamp."""
  txId: int
  """Transaction identifier."""
  type: Literal['ROLL_IN', 'ROLL_OUT']
  """Transfer direction."""


class MarginTransferHistory(TypedDict):
  """Margin account transfer history, in descending order."""

  rows: list[MarginTransfer]
  """Transfer records."""
  total: int
  """Total number of matching records across all pages."""


class TransferHistory(RpcEndpoint):
  """Query this account's cross (or, with `isolatedSymbol` set, isolated) margin transfer history. Results are returned in descending order. Returns the last 7 days by default."""

  async def transfer_history(
    self,
    *,
    asset: str | None = None,
    type: Literal['ROLL_IN', 'ROLL_OUT'] | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    current: int | None = None,
    size: int | None = None,
    isolated_symbol: str | None = None,
    validate: bool | None = None,
  ) -> MarginTransferHistory:
    """Query this account's cross (or, with `isolatedSymbol` set, isolated) margin transfer history. Results are returned in descending order. Returns the last 7 days by default.

    Args:
      asset: Asset to filter by, e.g. BNB. Omit to return all assets.
      type: Transfer direction filter.
      start_time: UTC millisecond epoch start of the queried window.
      end_time: UTC millisecond epoch end of the queried window.
      current: Page number, starting from 1.
      size: Number of records per page.
      isolated_symbol: Isolated margin symbol. Omit to query cross margin transfer history; set to query an isolated margin symbol's transfer history instead.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/transfer#get-cross-margin-transfer-history)
    """
    params = {}
    if asset is not None:
      params['asset'] = asset
    if type is not None:
      params['type'] = type
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    if isolated_symbol is not None:
      params['isolatedSymbol'] = isolated_symbol
    _Response = MarginTransferHistory
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/margin/transfer',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def transfer_history_paged(
    self,
    *,
    asset: str | None = None,
    type: Literal['ROLL_IN', 'ROLL_OUT'] | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    size: int | None = None,
    isolated_symbol: str | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[MarginTransferHistory]:
    """Yield successive pages of `transfer_history`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.transfer_history(
        asset=asset,
        type=type,
        start_time=start_time,
        end_time=end_time,
        size=size,
        isolated_symbol=isolated_symbol,
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
