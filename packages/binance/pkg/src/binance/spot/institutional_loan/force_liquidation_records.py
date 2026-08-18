from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class ForceLiquidationLiability(TypedDict):
  """One outstanding liability entry at liquidation."""

  assetName: NotRequired[str]
  """Liability asset name."""
  principal: NotRequired[str]
  """Outstanding principal."""
  interest: NotRequired[str]
  """Outstanding interest."""


class ForceLiquidationMemberSnapshot(TypedDict):
  """One member account's snapshot at liquidation."""

  subEmail: NotRequired[str]
  """Sub-account registered email."""
  memberType: NotRequired[Literal['CREDIT', 'COLLATERAL']]
  """Member type."""
  walletType: NotRequired[Literal['SPOT', 'PORTFOLIO_MARGIN', 'CROSS_MARGIN']]
  """Wallet type."""
  netEquity: NotRequired[str]
  """Account net equity."""
  maintainMargin: NotRequired[str]
  """Account maintenance margin."""


class ForceLiquidationSnapshot(TypedDict):
  """Snapshot of the risk unit's members and liabilities at liquidation."""

  snapshots: NotRequired[list[ForceLiquidationMemberSnapshot]]
  """Per-member account snapshots at liquidation."""
  liabilities: NotRequired[list[ForceLiquidationLiability]]
  """Outstanding liabilities by asset at liquidation."""


class ForceLiquidationRecord(TypedDict):
  """One force liquidation record."""

  groupId: NotRequired[int]
  """Risk unit unique identifier."""
  startLtv: NotRequired[int]
  """The risk unit's LTV at the start of the liquidation."""
  endLtv: NotRequired[int]
  """The risk unit's LTV at the end of the liquidation."""
  liquidationStartTime: NotRequired[int]
  """Liquidation start timestamp, in milliseconds."""
  liquidationEndTime: NotRequired[int]
  """Liquidation end timestamp, in milliseconds."""
  totalNetEquity: NotRequired[str]
  """Sum of equity across all Portfolio Margin sub-accounts, plus (collateral value minus liability and interest) across all Cross Margin accounts, plus free accepted tokens in Spot."""
  totalMaintenanceMargin: NotRequired[str]
  """Aggregated maintenance margin."""
  totalLiability: NotRequired[str]
  """Outstanding loan principal plus outstanding loan interest."""
  liquidationSnapshot: NotRequired[ForceLiquidationSnapshot]


class ForceLiquidationRecordsPage(TypedDict):
  """One page of risk unit force liquidation records."""

  total: NotRequired[int]
  """Total number of risk units returned by the query."""
  rows: NotRequired[list[ForceLiquidationRecord]]
  """Matching force liquidation records."""


class ForceLiquidationRecords(RpcEndpoint):
  """Get institutional loan risk unit force liquidation records. Callable only with the credit account API key. The credit account can query currently activated and closed risk units using `groupId`; if omitted, only currently activated risk units are returned. Responses are returned in descending order. If neither `startTime` nor `endTime` is provided, data from the last 7 days is returned by default; `startTime` defaults to `endTime` minus 7 days and `endTime` defaults to the current time. The span between `startTime` and `endTime` must not exceed 100 days."""

  async def force_liquidation_records(
    self,
    *,
    group_id: int | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> ForceLiquidationRecordsPage:
    """Get institutional loan risk unit force liquidation records. Callable only with the credit account API key. The credit account can query currently activated and closed risk units using `groupId`; if omitted, only currently activated risk units are returned. Responses are returned in descending order. If neither `startTime` nor `endTime` is provided, data from the last 7 days is returned by default; `startTime` defaults to `endTime` minus 7 days and `endTime` defaults to the current time. The span between `startTime` and `endTime` must not exceed 100 days.

    Args:
      group_id: Risk unit unique identifier.
      start_time: Start time in milliseconds.
      end_time: End time in milliseconds.
      current: Current page number. Starts from 1.
      size: Number of records per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-institutional-loan/api/rest-api/trade#get-risk-unit-force-liquidation-record)
    """
    params = {}
    if group_id is not None:
      params['groupId'] = group_id
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    _Response = ForceLiquidationRecordsPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/margin/loan-group/force-liquidation',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def force_liquidation_records_paged(
    self,
    *,
    group_id: int | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[ForceLiquidationRecordsPage]:
    """Yield successive pages of `force_liquidation_records`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.force_liquidation_records(
        group_id=group_id,
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
