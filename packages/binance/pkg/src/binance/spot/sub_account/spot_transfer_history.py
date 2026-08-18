from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


SubAccountSpotTransferKeywords = TypedDict(
  'SubAccountSpotTransferKeywords', {'from': NotRequired[str]}
)
"""
- `from`: Email of the sending account.
"""


class SubAccountSpotTransfer(SubAccountSpotTransferKeywords):
  """One spot asset transfer between sub-accounts."""

  to: NotRequired[str]
  """Email of the receiving account."""
  asset: NotRequired[str]
  """Asset transferred."""
  qty: NotRequired[str]
  """Amount transferred."""
  status: NotRequired[str]
  """Transfer status."""
  tranId: NotRequired[int]
  """Transfer id."""
  time: NotRequired[int]
  """Time the transfer was executed."""


class SpotTransferHistory(RpcEndpoint):
  """Query the history of spot asset transfers between sub-accounts (or between a sub-account and the master account), for the master account."""

  async def __call__(
    self,
    *,
    from_email: str | None = None,
    to_email: str | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    page: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[SubAccountSpotTransfer]:
    """Query the history of spot asset transfers between sub-accounts (or between a sub-account and the master account), for the master account.

    Args:
      from_email: Filter to transfers sent from this email. Cannot be sent together with `toEmail`.
      to_email: Filter to transfers sent to this email. Cannot be sent together with `fromEmail`.
      start_time: Start of the query window.
      end_time: End of the query window.
      page: Page number.
      limit: Page size. The upstream docs state a default of 500 and a maximum of 200 for this parameter, which is internally contradictory; left unresolved pending a live call (spec-authoring rule 7).

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/asset-management#query-sub-account-spot-asset-transfer-history)
    """
    params = {}
    if from_email is not None:
      params['fromEmail'] = from_email
    if to_email is not None:
      params['toEmail'] = to_email
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if page is not None:
      params['page'] = page
    if limit is not None:
      params['limit'] = limit
    _Response = list[SubAccountSpotTransfer]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/sub-account/sub/transfer/history',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def paged(
    self,
    *,
    from_email: str | None = None,
    to_email: str | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[list[SubAccountSpotTransfer]]:
    """Yield successive pages of this endpoint.

    Requests `page` from 1 upwards and stops on the first page shorter than `limit`, or
    after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.__call__(
        from_email=from_email,
        to_email=to_email,
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
      if not response or (limit is not None and len(response) < limit):
        break
      page += 1
