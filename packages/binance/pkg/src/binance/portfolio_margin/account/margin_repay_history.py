from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmMarginRepayRecordRows(TypedDict):
  """PmMarginRepayRecordRows."""

  amount: NotRequired[str]
  """Total amount repaid."""
  asset: NotRequired[str]
  """asset name."""
  interest: NotRequired[str]
  """Interest repaid."""
  principal: NotRequired[str]
  """Principal repaid."""
  status: NotRequired[str]
  """one of PENDING (pending execution), CONFIRMED (successfully execution), FAILED (execution failed, nothing happened to your account)."""
  timestamp: NotRequired[int]
  """Timestamp."""
  txId: NotRequired[int]
  """Tx ID."""


class PmMarginRepayRecord(TypedDict):
  """Query margin repay record."""

  rows: NotRequired[list[PmMarginRepayRecordRows]]
  """Rows."""
  total: NotRequired[int]
  """Total."""


class MarginRepayHistory(RpcEndpoint):
  """Query Margin repay Record"""

  async def margin_repay_history(
    self,
    *,
    asset: str,
    tx_id: int | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    current: int | None = None,
    size: int | None = None,
    archived: Literal['true', 'false'] | None = None,
    validate: bool | None = None,
  ) -> PmMarginRepayRecord:
    """Query margin repay record.

    Args:
      asset: Asset name.
      tx_id: the `tranId` in `POST /papi/v1/repayLoan`.
      start_time: Timestamp in ms to get funding from INCLUSIVE.
      end_time: Timestamp in ms to get funding until INCLUSIVE.
      current: Current page number.
      size: Number of results returned.
      archived: Set to true to query archived data from 6 months ago.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#query-margin-repay-record)
    """
    params: dict = {
      'asset': asset,
    }
    if tx_id is not None:
      params['txId'] = tx_id
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    if archived is not None:
      params['archived'] = archived
    _Response = PmMarginRepayRecord
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/margin/repayLoan',
      params=params,
      validator=_validator,
      validate=validate,
    )
