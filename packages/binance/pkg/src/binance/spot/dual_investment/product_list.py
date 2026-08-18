from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class DualInvestmentProduct(TypedDict):
  """One offered Dual Investment product."""

  id: NotRequired[str]
  """Product identifier, passed to spot.dual_investment.subscribe."""
  investCoin: NotRequired[str]
  """Asset used for subscribing."""
  exercisedCoin: NotRequired[str]
  """Target exercised asset."""
  strikePrice: NotRequired[str]
  """Strike price, as a decimal string."""
  duration: NotRequired[int]
  """Product duration in days."""
  settleDate: NotRequired[int]
  """Millisecond epoch settlement date."""
  purchaseDecimal: NotRequired[int]
  """Decimal precision accepted for the subscription amount."""
  purchaseEndTime: NotRequired[int]
  """Millisecond epoch time after which the product can no longer be subscribed to."""
  canPurchase: NotRequired[bool]
  """Whether the product can be subscribed to currently."""
  apr: NotRequired[str]
  """Annual percentage rate, as a decimal string."""
  orderId: NotRequired[int]
  """Order identifier, passed to spot.dual_investment.subscribe."""
  minAmount: NotRequired[str]
  """Minimum subscription amount, as a decimal string."""
  maxAmount: NotRequired[str]
  """Maximum subscription amount, as a decimal string."""
  createTimestamp: NotRequired[int]
  """Millisecond epoch time the product was created."""
  optionType: NotRequired[Literal['CALL', 'PUT']]
  """Product option type."""
  isAutoCompoundEnable: NotRequired[bool]
  """Whether auto-compound is enabled for this product."""
  autoCompoundPlanList: NotRequired[list[str]]
  """Auto-compound plans available for this product."""


class DualInvestmentProductPage(TypedDict):
  """One page of currently offered Dual Investment products."""

  total: NotRequired[int]
  """Total number of matching products."""
  list: NotRequired[list[DualInvestmentProduct]]
  """Matching products on this page."""


class ProductList(RpcEndpoint):
  """Get the list of currently offered Dual Investment products."""

  async def product_list(
    self,
    *,
    option_type: Literal['CALL', 'PUT'],
    exercised_coin: str,
    invest_coin: str,
    page_size: int | None = None,
    page_index: int | None = None,
    recv_window: int | None = None,
    validate: bool | None = None,
  ) -> DualInvestmentProductPage:
    """Get the list of currently offered Dual Investment products.

    Args:
      option_type: Product option type. Determines how exercisedCoin/investCoin should be paired: for a high-sell product (call option), optionType=CALL with exercisedCoin the quote asset and investCoin the base asset; for a low-buy product (put option), optionType=PUT with exercisedCoin the base asset and investCoin the quote asset.
      exercised_coin: Target exercised asset.
      invest_coin: Asset used for subscribing.
      page_size: Number of records per page.
      page_index: Page index to return.
      recv_window: Request validity window in milliseconds. Must not exceed 60000.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-dual-investment/api/rest-api/market-data#get-dual-investment-product-list)
    """
    params: dict = {
      'optionType': option_type,
      'exercisedCoin': exercised_coin,
      'investCoin': invest_coin,
    }
    if page_size is not None:
      params['pageSize'] = page_size
    if page_index is not None:
      params['pageIndex'] = page_index
    if recv_window is not None:
      params['recvWindow'] = recv_window
    _Response = DualInvestmentProductPage
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/sapi/v1/dci/product/list',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def product_list_paged(
    self,
    *,
    option_type: Literal['CALL', 'PUT'],
    exercised_coin: str,
    invest_coin: str,
    page_size: int | None = None,
    recv_window: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[DualInvestmentProductPage]:
    """Yield successive pages of `product_list`.

    Requests `pageIndex` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    page_index = 1
    pages = 0
    while True:
      response = await self.product_list(
        option_type=option_type,
        exercised_coin=exercised_coin,
        invest_coin=invest_coin,
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
      if total is None or page_size is None or pages * page_size >= total:
        break
      page_index += 1
