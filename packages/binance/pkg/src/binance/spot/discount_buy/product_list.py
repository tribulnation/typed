from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class DiscountBuyProduct(TypedDict):
  """One offered Discount Buy product."""

  id: NotRequired[str]
  """Product identifier, passed as `projectId` to `spot.discount_buy.subscribe`."""
  investAsset: NotRequired[str]
  """Subscription (stablecoin) asset."""
  targetAsset: NotRequired[str]
  """Target (non-stablecoin) asset."""
  strikePrice: NotRequired[str]
  """Strike price of the accumulator, as a decimal string."""
  knockoutPrice: NotRequired[str]
  """Knock-out price of the accumulator, as a decimal string."""
  duration: NotRequired[int]
  """Product duration in days."""
  settleDate: NotRequired[int]
  """Millisecond epoch settlement date."""
  purchaseDecimal: NotRequired[int]
  """Decimal precision accepted for the subscription amount."""
  purchaseEndTime: NotRequired[int]
  """Millisecond epoch time subscription closes."""
  canPurchase: NotRequired[bool]
  """Whether the product can be subscribed to right now."""
  knockOutApr: NotRequired[str]
  """Annual percentage rate if the product knocks out, as a decimal string."""
  orderId: NotRequired[int]
  """Order identifier, passed as `orderId` to `spot.discount_buy.subscribe`."""
  minAmount: NotRequired[str]
  """Minimum subscription amount, as a decimal string."""
  maxAmount: NotRequired[str]
  """Maximum subscription amount, as a decimal string."""
  createTimestamp: NotRequired[int]
  """Millisecond epoch time the product was created."""


class DiscountBuyProductPage(TypedDict):
  """One page of currently offered Discount Buy products."""

  total: NotRequired[int]
  """Total number of matching products."""
  list: NotRequired[list[DiscountBuyProduct]]
  """Matching products on this page."""


class ProductList(RpcEndpoint):
  """Get the list of currently offered Discount Buy (Advanced Earn accumulator) products."""

  async def product_list(
    self,
    *,
    target_asset: str | None = None,
    invest_asset: str | None = None,
    page_size: int,
    page_index: int,
    recv_window: int | None = None,
    validate: bool | None = None,
  ) -> DiscountBuyProductPage:
    """Get the list of currently offered Discount Buy (Advanced Earn accumulator) products.

    Args:
      target_asset: Restrict results to this target (non-stablecoin) asset.
      invest_asset: Restrict results to this subscription (stablecoin) asset.
      page_size: Number of records per page.
      page_index: Page index to return, starting from 1.
      recv_window: Number of milliseconds after `timestamp` the request remains valid. Must not exceed 60000.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-discount-buy/api/rest-api/market-data#get-discount-buy-product-list)
    """
    params: dict = {
      'pageSize': page_size,
      'pageIndex': page_index,
    }
    if target_asset is not None:
      params['targetAsset'] = target_asset
    if invest_asset is not None:
      params['investAsset'] = invest_asset
    if recv_window is not None:
      params['recvWindow'] = recv_window
    _Response = DiscountBuyProductPage
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/sapi/v1/accumulator/product/list',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def product_list_paged(
    self,
    *,
    target_asset: str | None = None,
    invest_asset: str | None = None,
    page_size: int,
    recv_window: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[DiscountBuyProductPage]:
    """Yield successive pages of `product_list`.

    Requests `pageIndex` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    page_index = 1
    pages = 0
    while True:
      response = await self.product_list(
        target_asset=target_asset,
        invest_asset=invest_asset,
        page_size=page_size,
        recv_window=recv_window,
        page_index=page_index,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or pages * page_size >= total:
        break
      page_index += 1
