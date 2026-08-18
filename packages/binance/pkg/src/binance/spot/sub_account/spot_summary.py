from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SubAccountSpotAssetTotal(TypedDict):
  """One sub-account's total spot asset value."""

  email: NotRequired[str]
  """Sub-account email."""
  totalAsset: NotRequired[str]
  """Total spot asset value, in BTC."""


class SubAccountSpotAssetsSummary(TypedDict):
  """BTC-valued spot asset summary."""

  totalCount: NotRequired[int]
  """Total number of sub-accounts matching the query."""
  masterAccountTotalAsset: NotRequired[str]
  """Master account's total spot asset value, in BTC."""
  spotSubUserAssetBtcVoList: NotRequired[list[SubAccountSpotAssetTotal]]
  """Per-sub-account totals on this page."""


class SpotSummary(RpcEndpoint):
  """Get a BTC-valued summary of sub-accounts' spot assets, for the master account."""

  async def __call__(
    self,
    *,
    email: str | None = None,
    page: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> SubAccountSpotAssetsSummary:
    """Get a BTC-valued summary of sub-accounts' spot assets, for the master account.

    Args:
      email: Filter to one sub-account's email.
      page: Page number.
      size: Page size.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/asset-management#query-sub-account-spot-assets-summary)
    """
    params = {}
    if email is not None:
      params['email'] = email
    if page is not None:
      params['page'] = page
    if size is not None:
      params['size'] = size
    _Response = SubAccountSpotAssetsSummary
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/sub-account/spotSummary',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def paged(
    self,
    *,
    email: str | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[SubAccountSpotAssetsSummary]:
    """Yield successive pages of this endpoint.

    Requests `page` from 1 upwards and stops once it has covered the `totalCount` items
    the response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.__call__(
        email=email, size=size, page=page, validate=validate
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('totalCount') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or size is None or pages * size >= total:
        break
      page += 1
