from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SoftStakingProduct(TypedDict):
  """One available Soft Staking product."""

  asset: NotRequired[str]
  """Underlying asset of the Soft Staking product."""
  minAmount: NotRequired[str]
  """Minimum amount stakeable, as a decimal string."""
  maxCap: NotRequired[str]
  """Maximum total capacity of the product, as a decimal string."""
  apr: NotRequired[str]
  """Annual percentage rate, as a decimal string."""
  stakedAmount: NotRequired[str]
  """This account's currently staked amount in this product, as a decimal string."""
  totalProfit: NotRequired[str]
  """This account's total accrued profit from this product, as a decimal string."""


class SoftStakingProductListPage(TypedDict):
  """One page of available Soft Staking products, plus this account's overall Soft Staking status."""

  status: NotRequired[bool]
  """Whether this account currently has Soft Staking enabled."""
  totalRewardsUsdt: NotRequired[str]
  """This account's total Soft Staking rewards across all assets, denominated in USDT, as a decimal string."""
  rows: NotRequired[list[SoftStakingProduct]]
  """Matching products on this page."""
  total: NotRequired[int]
  """Total number of matching records."""


class List(RpcEndpoint):
  """Get the available Soft Staking product list."""

  async def __call__(
    self,
    *,
    asset: str | None = None,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> SoftStakingProductListPage:
    """Get the available Soft Staking product list.

    Args:
      asset: Restrict results to the Soft Staking product for this underlying asset.
      current: Page index, starting from 1.
      size: Number of results per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-staking/api/rest-api/soft-staking#get-soft-staking-product-list)
    """
    params = {}
    if asset is not None:
      params['asset'] = asset
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    _Response = SoftStakingProductListPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/soft-staking/list',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def paged(
    self,
    *,
    asset: str | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[SoftStakingProductListPage]:
    """Yield successive pages of this endpoint.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.__call__(
        asset=asset, size=size, current=current, validate=validate
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
