from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class NftAsset(TypedDict):
  """One held NFT."""

  network: NotRequired[str]
  """Blockchain network the token lives on, e.g. BSC."""
  contractAddress: NotRequired[str]
  """NFT contract address."""
  tokenId: NotRequired[str]
  """NFT token identifier."""


class NftAssetHoldings(TypedDict):
  """This account's current NFT holdings."""

  total: NotRequired[int]
  """Total number of held NFTs."""
  list: NotRequired[list[NftAsset]]
  """Held NFTs."""


class Asset(RpcEndpoint):
  """Query this account's current NFT holdings."""

  async def asset(
    self,
    *,
    limit: int | None = None,
    page: int | None = None,
    validate: bool | None = None,
  ) -> NftAssetHoldings:
    """Query this account's current NFT holdings.

    Args:
      limit: Number of records per page.
      page: Page number.

    References:
      - [Official docs](https://developers.binance.com/docs/nft/rest-api/Get-NFT-Asset)
    """
    params = {}
    if limit is not None:
      params['limit'] = limit
    if page is not None:
      params['page'] = page
    _Response = NftAssetHoldings
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/nft/user/getAsset',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def asset_paged(
    self,
    *,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[NftAssetHoldings]:
    """Yield successive pages of `asset`.

    Requests `page` from 1 upwards and stops once it has covered the `total` items the
    response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.asset(limit=limit, page=page, validate=validate)
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or limit is None or pages * limit >= total:
        break
      page += 1
