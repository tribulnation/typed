from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FiatOrder(TypedDict):
  """One fiat deposit or withdrawal order."""

  orderNo: NotRequired[str]
  """Order identifier."""
  fiatCurrency: NotRequired[str]
  """Fiat currency of the order."""
  indicatedAmount: NotRequired[str]
  """Requested amount, as a decimal string."""
  amount: NotRequired[str]
  """Settled amount, as a decimal string."""
  totalFee: NotRequired[str]
  """Total fee charged, as a decimal string."""
  method: NotRequired[str]
  """Payment method used."""
  status: NotRequired[
    Literal[
      'Processing',
      'Failed',
      'Successful',
      'Finished',
      'Refunding',
      'Refunded',
      'Refund Failed',
      'Order Partial Credit Stopped',
    ]
  ]
  """Order status."""
  createTime: NotRequired[int]
  """Millisecond epoch time the order was created."""
  updateTime: NotRequired[int]
  """Millisecond epoch time the order was last updated."""


class FiatOrderHistoryPage(TypedDict):
  """One page of this account's fiat deposit/withdraw order history."""

  code: NotRequired[str]
  """Response code. "000000" indicates success."""
  message: NotRequired[str]
  """Response message."""
  data: NotRequired[list[FiatOrder]]
  """Matching orders on this page."""
  total: NotRequired[int]
  """Total number of matching orders."""
  success: NotRequired[bool]
  """Whether the call succeeded."""


class Orders(RpcEndpoint):
  """Get this account's fiat deposit/withdraw order history. If beginTime/endTime are omitted, the recent 30 days are returned."""

  async def orders(
    self,
    *,
    transaction_type: Literal['0', '1'],
    begin_time: int | None = None,
    end_time: int | None = None,
    page: int | None = None,
    rows: int | None = None,
    validate: bool | None = None,
  ) -> FiatOrderHistoryPage:
    """Get this account's fiat deposit/withdraw order history. If beginTime/endTime are omitted, the recent 30 days are returned.

    Args:
      transaction_type: Direction of the orders to return.
      begin_time: Millisecond epoch start of the queried window.
      end_time: Millisecond epoch end of the queried window.
      page: Page number to return.
      rows: Number of records per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-fiat/api/rest-api/~#get-fiat-deposit-withdraw-history)
    """
    params: dict = {
      'transactionType': transaction_type,
    }
    if begin_time is not None:
      params['beginTime'] = begin_time
    if end_time is not None:
      params['endTime'] = end_time
    if page is not None:
      params['page'] = page
    if rows is not None:
      params['rows'] = rows
    _Response = FiatOrderHistoryPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/fiat/orders',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def orders_paged(
    self,
    *,
    transaction_type: Literal['0', '1'],
    begin_time: int | None = None,
    end_time: int | None = None,
    rows: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[FiatOrderHistoryPage]:
    """Yield successive pages of `orders`.

    Requests `page` from 1 upwards and stops once it has covered the `total` items the
    response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.orders(
        transaction_type=transaction_type,
        begin_time=begin_time,
        end_time=end_time,
        rows=rows,
        page=page,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or rows is None or pages * rows >= total:
        break
      page += 1
