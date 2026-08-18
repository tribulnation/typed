from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


SubAccountFuturesInternalTransferKeywords = TypedDict(
  'SubAccountFuturesInternalTransferKeywords', {'from': NotRequired[str]}
)
"""
- `from`: Email of the sending account.
"""


class SubAccountFuturesInternalTransfer(SubAccountFuturesInternalTransferKeywords):
  """One futures asset transfer between sub-accounts."""

  to: NotRequired[str]
  """Email of the receiving account."""
  asset: NotRequired[str]
  """Asset transferred."""
  qty: NotRequired[str]
  """Amount transferred."""
  tranId: NotRequired[int]
  """Transfer id."""
  time: NotRequired[int]
  """Time the transfer was executed."""


class SubAccountFuturesInternalTransferHistory(TypedDict):
  """Matching transfer records."""

  success: NotRequired[bool]
  """Whether the query succeeded."""
  futuresType: NotRequired[int]
  """Which futures product: `1` = USD-M (USDT-margined) futures, `2` = COIN-M (coin-margined) futures."""
  transfers: NotRequired[list[SubAccountFuturesInternalTransfer]]
  """Transfer records on this page."""


class FuturesInternalTransferHistory(RpcEndpoint):
  """Query the history of futures asset transfers between sub-accounts, for the master account."""

  async def __call__(
    self,
    *,
    email: str,
    futures_type: int,
    start_time: int | None = None,
    end_time: int | None = None,
    page: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> SubAccountFuturesInternalTransferHistory:
    """Query the history of futures asset transfers between sub-accounts, for the master account.

    Args:
      email: Sub-account email (either side of the transfer).
      futures_type: Which futures product: `1` = USD-M (USDT-margined) futures, `2` = COIN-M (coin-margined) futures.
      start_time: Start of the query window. Cannot be earlier than one month ago.
      end_time: End of the query window.
      page: Page number.
      limit: Page size.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/asset-management#query-sub-account-futures-asset-transfer-history)
    """
    params: dict = {
      'email': email,
      'futuresType': futures_type,
    }
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if page is not None:
      params['page'] = page
    if limit is not None:
      params['limit'] = limit
    _Response = SubAccountFuturesInternalTransferHistory
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/sub-account/futures/internalTransfer',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def paged(
    self,
    *,
    email: str,
    futures_type: int,
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[SubAccountFuturesInternalTransferHistory]:
    """Yield successive pages of this endpoint.

    Requests `page` from 1 upwards and stops on the first page shorter than `limit`, or
    after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.__call__(
        email=email,
        futures_type=futures_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        page=page,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      rows = response.get('transfers') if response is not None else None
      if not rows or (limit is not None and len(rows) < limit):
        break
      page += 1
