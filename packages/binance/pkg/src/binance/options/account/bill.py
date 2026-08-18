from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class FundingFlowRecord(TypedDict):
  """One account funding-flow record."""

  id: NotRequired[int]
  """Record ID."""
  asset: NotRequired[str]
  """Asset type."""
  amount: NotRequired[str]
  """Amount. Positive numbers represent inflow, negative numbers represent outflow."""
  type: NotRequired[str]
  """Flow type, e.g. fees."""
  createDate: NotRequired[Timestamp]
  """Time the flow record was created."""


class Bill(RpcEndpoint):
  """Query account funding flows. Only supports querying data from the past 3 months."""

  async def bill(
    self,
    *,
    currency: Literal['USDT'],
    record_id: int | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[FundingFlowRecord]:
    """Query account funding flows. Only supports querying data from the past 3 months.

    Args:
      currency: Asset type. Only USDT is documented as supported.
      record_id: Return this recordId and subsequent data. Defaults to the latest data.
      start_time: Start time.
      end_time: End time.
      limit: Number of result sets returned.

    References:
      - [Official docs](https://developers.binance.com/docs/derivatives/option/account#account-funding-flow)
    """
    params: dict = {
      'currency': currency,
    }
    if record_id is not None:
      params['recordId'] = record_id
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if limit is not None:
      params['limit'] = limit
    _Response = list[FundingFlowRecord]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/eapi/v1/bill', params=params, validator=_validator, validate=validate
    )
