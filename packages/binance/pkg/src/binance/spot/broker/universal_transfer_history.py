from typing_extensions import AsyncIterator, Literal, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class BrokerUniversalTransferRecord(TypedDict):
  """One historical universal transfer."""

  toId: str
  """Destination account."""
  asset: str
  """Asset transferred."""
  qty: str
  """Quantity transferred."""
  time: Timestamp
  """Time the transfer was processed."""
  status: str
  """Transfer status. Documented example is `SUCCESS`; the venue does not declare this as a closed enum."""
  txnId: str
  """Transfer transaction identifier."""
  clientTranId: str
  """Caller-supplied idempotency id, if any."""
  fromAccountType: Literal['SPOT', 'USDT_FUTURE', 'COIN_FUTURE']
  """Source account type."""
  toAccountType: Literal['SPOT', 'USDT_FUTURE', 'COIN_FUTURE']
  """Destination account type."""


class UniversalTransferHistory(RpcEndpoint):
  """Query Universal Transfer History"""

  async def universal_transfer_history(
    self,
    *,
    from_id: str | None = None,
    to_id: str | None = None,
    client_tran_id: str | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    page: int | None = None,
    limit: int | None = None,
    show_all_status: bool | None = None,
    validate: bool | None = None,
  ) -> list[BrokerUniversalTransferRecord]:
    """Get historical universal transfers across account/product types.

    Args:
      from_id: Filter by source account.
      to_id: Filter by destination account.
      client_tran_id: Filter by caller-supplied idempotency id.
      start_time: Start of the query window, UTC ms.
      end_time: End of the query window, UTC ms.
      page: Page number, 1-indexed. Default 1.
      limit: Records per page. Default 500, max 500.
      show_all_status: Include transfers of every status, not just successful ones.

    References:
      - [Official docs](https://binance-docs.github.io/Brokerage-API/Brokerage_Operation_Endpoints/)
    """
    params = {}
    if from_id is not None:
      params['fromId'] = from_id
    if to_id is not None:
      params['toId'] = to_id
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
    if show_all_status is not None:
      params['showAllStatus'] = show_all_status
    _Response = list[BrokerUniversalTransferRecord]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/broker/universalTransfer',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def universal_transfer_history_paged(
    self,
    *,
    from_id: str | None = None,
    to_id: str | None = None,
    client_tran_id: str | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    limit: int | None = None,
    show_all_status: bool | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[list[BrokerUniversalTransferRecord]]:
    """Yield successive pages of `universal_transfer_history`.

    Requests `page` from 1 upwards and stops on the first page shorter than `limit`, or
    after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.universal_transfer_history(
        from_id=from_id,
        to_id=to_id,
        client_tran_id=client_tran_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        show_all_status=show_all_status,
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
