from typing_extensions import AsyncIterator, Literal, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


BrokerFuturesTransferRecordKeywords = TypedDict(
  'BrokerFuturesTransferRecordKeywords', {'from': str}
)
"""
- `from`: Source account. Empty when transferring from the master account.
"""


class BrokerFuturesTransferRecord(BrokerFuturesTransferRecordKeywords):
  """One historical futures transfer."""

  to: str
  """Destination account."""
  asset: str
  """Asset transferred."""
  qty: str
  """Quantity transferred."""
  tranId: str
  """Transfer transaction identifier."""
  clientTranId: str
  """Caller-supplied idempotency id, if any."""
  time: Timestamp
  """Time the transfer was processed."""


class BrokerFuturesTransferHistory(TypedDict):
  """Historical futures transfers for one sub-account."""

  success: bool
  """Whether the query succeeded."""
  futuresType: Literal[1, 2]
  """Futures product queried."""
  transfers: list[BrokerFuturesTransferRecord]
  """Historical futures transfers."""


class SubAccountTransferHistoryFutures(RpcEndpoint):
  """Query Sub Account Transfer History (FUTURES)"""

  async def sub_account_transfer_history_futures(
    self,
    *,
    sub_account_id: str,
    futures_type: Literal[1, 2],
    client_tran_id: str | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    page: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> BrokerFuturesTransferHistory:
    """Get historical futures transfers between the master account and a sub-account.

    Args:
      sub_account_id: Sub-account identifier.
      futures_type: Futures product to filter by.
      client_tran_id: Filter by caller-supplied idempotency id.
      start_time: Start of the query window, UTC ms. Defaults to 30 days of records.
      end_time: End of the query window, UTC ms. Defaults to 30 days of records.
      page: Page number, 1-indexed. Default 1.
      limit: Records per page. Default 50, max 500.

    References:
      - [Official docs](https://binance-docs.github.io/Brokerage-API/Brokerage_Operation_Endpoints/)
    """
    params: dict = {
      'subAccountId': sub_account_id,
      'futuresType': futures_type,
    }
    if client_tran_id is not None:
      params['clientTranId'] = client_tran_id
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if page is not None:
      params['page'] = page
    if limit is not None:
      params['limit'] = limit
    _Response = BrokerFuturesTransferHistory
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/broker/transfer/futures',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def sub_account_transfer_history_futures_paged(
    self,
    *,
    sub_account_id: str,
    futures_type: Literal[1, 2],
    client_tran_id: str | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[BrokerFuturesTransferHistory]:
    """Yield successive pages of `sub_account_transfer_history_futures`.

    Requests `page` from 1 upwards and stops on the first page shorter than `limit`, or
    after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.sub_account_transfer_history_futures(
        sub_account_id=sub_account_id,
        futures_type=futures_type,
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
      rows = response.get('transfers') if response is not None else None
      if not rows or (limit is not None and len(rows) < limit):
        break
      page += 1
