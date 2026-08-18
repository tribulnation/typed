from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class NftToken(TypedDict):
  """One NFT token."""

  network: NotRequired[str]
  """Blockchain network the token lives on, e.g. BSC, ETH."""
  tokenId: NotRequired[str]
  """NFT token identifier."""
  contractAddress: NotRequired[str]
  """NFT contract address."""


class NftTransaction(TypedDict):
  """One NFT transaction, which may involve multiple tokens (e.g. a mystery box)."""

  orderNo: NotRequired[str]
  """Order identifier, prefixed with the `orderType` value it matches, e.g. `1_470502070600699904`."""
  tokens: NotRequired[list[NftToken]]
  """NFT tokens involved in this transaction."""
  tradeTime: NotRequired[int]
  """Millisecond epoch trade timestamp."""
  tradeAmount: NotRequired[str]
  """Trade amount."""
  tradeCurrency: NotRequired[str]
  """Currency the trade amount is denominated in."""


class NftTransactionHistory(TypedDict):
  """This account's NFT transaction history."""

  total: NotRequired[int]
  """Total number of matching records."""
  list: NotRequired[list[NftTransaction]]
  """NFT transactions."""


class TransactionHistory(RpcEndpoint):
  """Query this account's NFT transaction history (purchases, sales, royalty income, primary market orders, mint fees)."""

  async def transaction_history(
    self,
    *,
    order_type: Literal[0, 1, 2, 3, 4],
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    page: int | None = None,
    validate: bool | None = None,
  ) -> NftTransactionHistory:
    """Query this account's NFT transaction history (purchases, sales, royalty income, primary market orders, mint fees).

    Args:
      order_type: Transaction type filter.
      start_time: Millisecond epoch start of the queried window.
      end_time: Millisecond epoch end of the queried window.
      limit: Number of records per page.
      page: Page number.

    References:
      - [Official docs](https://developers.binance.com/docs/nft/rest-api/Get-NFT-Transaction-History)
    """
    params: dict = {
      'orderType': order_type,
    }
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if limit is not None:
      params['limit'] = limit
    if page is not None:
      params['page'] = page
    _Response = NftTransactionHistory
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/nft/history/transactions',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def transaction_history_paged(
    self,
    *,
    order_type: Literal[0, 1, 2, 3, 4],
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[NftTransactionHistory]:
    """Yield successive pages of `transaction_history`.

    Requests `page` from 1 upwards and stops once it has covered the `total` items the
    response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.transaction_history(
        order_type=order_type,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
        page=page,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or limit is None or pages * limit >= total:
        break
      page += 1
