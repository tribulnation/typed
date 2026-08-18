from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class OnChainYieldsLockedProductDetail(TypedDict):
  """Terms of the locked product."""

  asset: NotRequired[str]
  """Underlying asset of the locked product."""
  rewardAsset: NotRequired[str]
  """Asset the base rewards are paid in."""
  duration: NotRequired[int]
  """Lock duration in days."""
  renewable: NotRequired[bool]
  """Whether the position can be configured to auto-renew at maturity."""
  isSoldOut: NotRequired[bool]
  """Whether the product's subscription quota is currently exhausted."""
  apr: NotRequired[str]
  """Annual percentage rate, as a decimal string."""
  status: NotRequired[str]
  """Product status."""
  subscriptionStartTime: NotRequired[int]
  """Millisecond epoch time the product became available for subscription."""
  canRedeemToFlex: NotRequired[bool]
  """Whether a position in this product can be redeemed early into a flexible position."""


class OnChainYieldsLockedProductQuota(TypedDict):
  """This account's subscription quota for the locked product."""

  totalPersonalQuota: NotRequired[str]
  """Total amount this account may subscribe to this product, as a decimal string."""
  minimum: NotRequired[str]
  """Minimum subscription amount, as a decimal string."""


class OnChainYieldsLockedProduct(TypedDict):
  """One available On-chain Yields locked product."""

  projectId: NotRequired[str]
  """Locked product identifier, used as `projectId` in subscribe/personal-left-quota/subscription-preview calls."""
  detail: NotRequired[OnChainYieldsLockedProductDetail]
  quota: NotRequired[OnChainYieldsLockedProductQuota]


class OnChainYieldsLockedProductListPage(TypedDict):
  """One page of available On-chain Yields locked products."""

  rows: NotRequired[list[OnChainYieldsLockedProduct]]
  """Matching records on this page."""
  total: NotRequired[int]
  """Total number of matching records."""


class List(RpcEndpoint):
  """Get the list of available On-chain Yields locked products."""

  async def __call__(
    self,
    *,
    asset: str | None = None,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> OnChainYieldsLockedProductListPage:
    """Get the list of available On-chain Yields locked products.

    Args:
      asset: Restrict results to locked products for this underlying asset.
      current: Page index, starting from 1.
      size: Number of results per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-staking/api/rest-api/on-chain-yields#get-on-chain-yields-locked-product-list)
    """
    params = {}
    if asset is not None:
      params['asset'] = asset
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    _Response = OnChainYieldsLockedProductListPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/onchain-yields/locked/list',
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
  ) -> AsyncIterator[OnChainYieldsLockedProductListPage]:
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
