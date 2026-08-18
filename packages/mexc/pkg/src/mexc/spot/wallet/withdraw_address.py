from mexc.core import Timestamp, timestamp as ts, validator
from typing_extensions import AsyncIterator, TypedDict
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class WithdrawAddressItem(TypedDict):
  """Withdrawal address."""
  coin: str | None
  """Asset."""
  network: str | None
  """Network."""
  address: str | None
  """Withdrawal address."""
  addressTag: str | None
  """Address label/tag."""
  memo: str | None
  """Address memo."""

class WithdrawAddressResponse(TypedDict):
  """Withdrawal address lookup response."""
  data: list[WithdrawAddressItem]
  """Withdrawal addresses."""
  totalRecords: int | None
  """Total records."""
  page: int | None
  """Current page."""
  totalPageNum: int | None
  """Total pages."""

Response: type[WithdrawAddressResponse | ErrorResponse] = WithdrawAddressResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class WithdrawAddress(AuthSpotMixin):
  async def withdraw_address(
    self, *,
    coin: str | None = None, page: int | None = None, limit: int | None = None,
    timestamp: Timestamp | None = None, validate: bool | None = None,
  ) -> WithdrawAddressResponse:
    """Returns saved withdrawal addresses for the signed account.

    Args:
      coin: Asset filter.
      page: Page number; default 1.
      limit: Records per page.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#withdraw-address-supporting-network)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if coin is not None:
      params['coin'] = coin
    if page is not None:
      params['page'] = page
    if limit is not None:
      params['limit'] = limit
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/capital/withdraw/address', params=params)
    return self.output(r.text, adapter, validate)

  async def withdraw_address_paged(
    self, *,
    coin: str | None = None, limit: int | None = None,
    timestamp: Timestamp | None = None, max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[WithdrawAddressResponse]:
    """Yield successive pages of `withdraw_address`.

    Requests `page` from 1 upwards and stops on the first page shorter than `limit`, or
    after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.withdraw_address(coin=coin, limit=limit, timestamp=timestamp, page=page, validate=validate)
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      rows = response.get('data') if response is not None else None
      if not rows or (limit is not None and len(rows) < limit):
        break
      page += 1
