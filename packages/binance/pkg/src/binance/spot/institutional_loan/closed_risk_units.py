from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class ClosedRiskUnitRecord(TypedDict):
  """One closed risk unit record."""

  groupId: NotRequired[int]
  """Risk unit unique identifier."""
  parentEmail: NotRequired[str]
  """Parent account email."""
  creditEmail: NotRequired[str]
  """Credit account email."""
  enabled: NotRequired[bool]
  """Risk unit status. `true` for enabled, `false` for disabled."""
  createTime: NotRequired[int]
  """Risk unit creation timestamp, in milliseconds."""
  closeTime: NotRequired[int]
  """Risk unit close timestamp, in milliseconds."""


class ClosedRiskUnitRecordsPage(TypedDict):
  """One page of closed risk unit records."""

  total: NotRequired[int]
  """Total number of risk units returned by the query."""
  rows: NotRequired[list[ClosedRiskUnitRecord]]
  """Matching closed risk unit records."""


class ClosedRiskUnits(RpcEndpoint):
  """Query closed institutional loan risk unit records. Callable only with the credit account API key."""

  async def closed_risk_units(
    self,
    *,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> ClosedRiskUnitRecordsPage:
    """Query closed institutional loan risk unit records. Callable only with the credit account API key.

    Args:
      current: Current page number. Starts from 1.
      size: Number of records per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-institutional-loan/api/rest-api/account#query-closed-risk-unit-record)
    """
    params = {}
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    _Response = ClosedRiskUnitRecordsPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/margin/loan-groups/closed',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def closed_risk_units_paged(
    self,
    *,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[ClosedRiskUnitRecordsPage]:
    """Yield successive pages of `closed_risk_units`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.closed_risk_units(
        size=size, current=current, validate=validate
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
