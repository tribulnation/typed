from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class PmMarginBorrowLoanInterestHistoryRows(TypedDict):
  """PmMarginBorrowLoanInterestHistoryRows."""

  txId: NotRequired[int]
  """Tx ID."""
  interestAccuredTime: NotRequired[Timestamp]
  """Interest Accured Time."""
  asset: NotRequired[str]
  """asset name."""
  rawAsset: NotRequired[str]
  """Raw Asset."""
  principal: NotRequired[str]
  """Principal repaid."""
  interest: NotRequired[str]
  """Interest repaid."""
  interestRate: NotRequired[str]
  """daily interest rate."""
  type: NotRequired[str]
  """Normal order type after trigger if appliable."""


class PmMarginBorrowLoanInterestHistory(TypedDict):
  """Get Margin Borrow/Loan Interest History."""

  rows: NotRequired[list[PmMarginBorrowLoanInterestHistoryRows]]
  """Rows."""
  total: NotRequired[int]
  """Total."""


class MarginInterestHistory(RpcEndpoint):
  """Get Margin Borrow/Loan Interest History"""

  async def margin_interest_history(
    self,
    *,
    asset: str | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    current: int | None = None,
    size: int | None = None,
    archived: Literal['true', 'false'] | None = None,
    validate: bool | None = None,
  ) -> PmMarginBorrowLoanInterestHistory:
    """Get Margin Borrow/Loan Interest History.

    Args:
      asset: Asset name.
      start_time: Timestamp in ms to get funding from INCLUSIVE.
      end_time: Timestamp in ms to get funding until INCLUSIVE.
      current: Current page number.
      size: Number of results returned.
      archived: Set to true to query archived data from 6 months ago.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-margin-borrow-loan-interest-history)
    """
    params = {}
    if asset is not None:
      params['asset'] = asset
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
    _Response = PmMarginBorrowLoanInterestHistory
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/papi/v1/margin/marginInterestHistory',
      params=params,
      validator=_validator,
      validate=validate,
    )
