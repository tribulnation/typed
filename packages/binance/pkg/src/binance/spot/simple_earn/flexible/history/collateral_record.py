from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FlexibleCollateralRecord(TypedDict):
  """One collateral event against a flexible product position."""

  amount: NotRequired[str]
  """Amount of the collateral event, as a decimal string."""
  productId: NotRequired[str]
  """Flexible product identifier the collateral was drawn from."""
  asset: NotRequired[str]
  """Asset moved as collateral."""
  createTime: NotRequired[int]
  """Millisecond epoch time the collateral event was recorded."""
  type: NotRequired[str]
  """Type of collateral event (e.g. pledging collateral for a crypto loan, or its release)."""
  productName: NotRequired[str]
  """Display name of the flexible product."""
  orderId: NotRequired[int]
  """Identifier of the order (e.g. loan order) this collateral event is associated with."""


class FlexibleCollateralRecordPage(TypedDict):
  """One page of this account's flexible-product collateral events."""

  rows: NotRequired[list[FlexibleCollateralRecord]]
  """Matching records on this page."""
  total: NotRequired[int]
  """Total number of matching records."""


class CollateralRecord(RpcEndpoint):
  """Get this account's history of collateral events (e.g. crypto-loan pledges) against Simple Earn flexible product positions."""

  async def collateral_record(
    self,
    *,
    product_id: str | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> FlexibleCollateralRecordPage:
    """Get this account's history of collateral events (e.g. crypto-loan pledges) against Simple Earn flexible product positions.

    Args:
      product_id: Restrict results to this flexible product.
      start_time: Millisecond epoch start of the queried window.
      end_time: Millisecond epoch end of the queried window.
      current: Currently querying page.
      size: Number of results per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#get-collateral-record)
    """
    params = {}
    if product_id is not None:
      params['productId'] = product_id
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    _Response = FlexibleCollateralRecordPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/simple-earn/flexible/history/collateralRecord',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def collateral_record_paged(
    self,
    *,
    product_id: str | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[FlexibleCollateralRecordPage]:
    """Yield successive pages of `collateral_record`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.collateral_record(
        product_id=product_id,
        start_time=start_time,
        end_time=end_time,
        size=size,
        current=current,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or size is None or pages * size >= total:
        break
      current += 1
