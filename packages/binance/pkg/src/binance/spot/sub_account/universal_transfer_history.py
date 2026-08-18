from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class UniversalTransferRecord(TypedDict):
  """One universal transfer."""

  tranId: NotRequired[int]
  """Transfer id."""
  fromEmail: NotRequired[str]
  """Email of the sending account."""
  toEmail: NotRequired[str]
  """Email of the receiving account."""
  asset: NotRequired[str]
  """Asset transferred."""
  amount: NotRequired[str]
  """Amount transferred."""
  createTimeStamp: NotRequired[int]
  """Time the transfer was created."""
  fromAccountType: NotRequired[
    Literal['SPOT', 'USDT_FUTURE', 'COIN_FUTURE', 'MARGIN', 'ISOLATED_MARGIN']
  ]
  """Account type transferred from."""
  toAccountType: NotRequired[
    Literal['SPOT', 'USDT_FUTURE', 'COIN_FUTURE', 'MARGIN', 'ISOLATED_MARGIN']
  ]
  """Account type transferred to."""
  status: NotRequired[str]
  """Transfer status."""
  clientTranId: NotRequired[str]
  """Caller-supplied transfer id, if one was given."""


class UniversalTransferHistory(TypedDict):
  """Matching universal transfer records."""

  result: NotRequired[list[UniversalTransferRecord]]
  """Transfer records on this page."""
  totalCount: NotRequired[int]
  """Total number of matching transfer records."""


class UniversalTransferHistoryEndpoint(RpcEndpoint):
  """Query universal transfer history, for the master account."""

  async def __call__(
    self,
    *,
    from_email: str | None = None,
    to_email: str | None = None,
    client_tran_id: str | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    page: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> UniversalTransferHistory:
    """Query universal transfer history, for the master account.

    Args:
      from_email: Filter to transfers sent from this email. Cannot be sent together with `toEmail`.
      to_email: Filter to transfers sent to this email. Cannot be sent together with `fromEmail`.
      client_tran_id: Filter by caller-supplied transfer id.
      start_time: Start of the query window.
      end_time: End of the query window.
      page: Page number.
      limit: Page size.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/asset-management#query-universal-transfer-history)
    """
    params = {}
    if from_email is not None:
      params['fromEmail'] = from_email
    if to_email is not None:
      params['toEmail'] = to_email
    if client_tran_id is not None:
      params['clientTranId'] = client_tran_id
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if page is not None:
      params['page'] = page
    if limit is not None:
      params['limit'] = limit
    _Response = UniversalTransferHistory
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/sub-account/universalTransfer',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def paged(
    self,
    *,
    from_email: str | None = None,
    to_email: str | None = None,
    client_tran_id: str | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[UniversalTransferHistory]:
    """Yield successive pages of this endpoint.

    Requests `page` from 1 upwards and stops once it has covered the `totalCount` items
    the response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.__call__(
        from_email=from_email,
        to_email=to_email,
        client_tran_id=client_tran_id,
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
      total = response.get('totalCount') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or limit is None or pages * limit >= total:
        break
      page += 1
