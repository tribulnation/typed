from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class ForceLiquidationTransferAsset(TypedDict):
  """One transferred asset amount."""

  assetName: NotRequired[str]
  """Name of the transferred asset."""
  amount: NotRequired[str]
  """Amount of the transferred asset."""


class ForceLiquidationTransfer(TypedDict):
  """One transfer made during the liquidation."""

  transferTime: NotRequired[int]
  """Transfer event timestamp, in milliseconds."""
  fromUid: NotRequired[str]
  """UID of the account transferring assets."""
  fromAccountType: NotRequired[Literal['SPOT', 'PORTFOLIO_MARGIN', 'CROSS_MARGIN']]
  """Account type of the transferring account."""
  toUid: NotRequired[str]
  """UID of the account receiving assets."""
  toAccountType: NotRequired[Literal['SPOT', 'PORTFOLIO_MARGIN', 'CROSS_MARGIN']]
  """Account type of the receiving account."""
  status: NotRequired[str]
  """Current transfer status."""
  assets: NotRequired[list[ForceLiquidationTransferAsset]]
  """Transferred assets."""


class ForceLiquidationTransferRecord(TypedDict):
  """One forced liquidation transfer record, grouped by liquidation event."""

  liquidationId: NotRequired[int]
  """Risk unit liquidation unique identifier."""
  liquidationTransferRecord: NotRequired[list[ForceLiquidationTransfer]]
  """Transfer records related to this liquidation."""


class ForceLiquidationTransferRecordsPage(TypedDict):
  """One page of forced liquidation transfer records."""

  total: NotRequired[int]
  """Total number of matching records."""
  rows: NotRequired[list[ForceLiquidationTransferRecord]]
  """Matching forced liquidation transfer records."""


class ForceLiquidationTransferRecords(RpcEndpoint):
  """Query transfer records made during institutional loan risk unit forced liquidation. Callable only with the credit account API key. Results are returned in descending order. If neither `startTime` nor `endTime` is provided, data from the last 7 days is returned by default; `startTime` defaults to `endTime` minus 7 days and `endTime` defaults to the current time. The span between `startTime` and `endTime` cannot exceed 100 days."""

  async def force_liquidation_transfer_records(
    self,
    *,
    start_time: int | None = None,
    end_time: int | None = None,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> ForceLiquidationTransferRecordsPage:
    """Query transfer records made during institutional loan risk unit forced liquidation. Callable only with the credit account API key. Results are returned in descending order. If neither `startTime` nor `endTime` is provided, data from the last 7 days is returned by default; `startTime` defaults to `endTime` minus 7 days and `endTime` defaults to the current time. The span between `startTime` and `endTime` cannot exceed 100 days.

    Args:
      start_time: Start time in milliseconds.
      end_time: End time in milliseconds.
      current: Current page number. Starts from 1.
      size: Number of records per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-institutional-loan/api/rest-api/transfer#query-risk-unit-forced-liquidation-transfer-records)
    """
    params = {}
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    _Response = ForceLiquidationTransferRecordsPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/margin/loan-group/force-liquidation-transfer-record',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def force_liquidation_transfer_records_paged(
    self,
    *,
    start_time: int | None = None,
    end_time: int | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[ForceLiquidationTransferRecordsPage]:
    """Yield successive pages of `force_liquidation_transfer_records`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.force_liquidation_transfer_records(
        start_time=start_time,
        end_time=end_time,
        size=size,
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
