from typing_extensions import AsyncIterator, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class BrokerSubAccountApiKeyInfo(TypedDict):
  """One sub-account API key."""

  subaccountId: str
  """Sub-account identifier."""
  apikey: str
  """API key."""
  canTrade: bool
  """Whether spot trading is enabled."""
  marginTrade: bool
  """Whether margin trading is enabled."""
  futuresTrade: bool
  """Whether futures trading is enabled."""


class SubAccountApiKey(RpcEndpoint):
  """Query Sub Account Api Key"""

  async def sub_account_api_key(
    self,
    *,
    sub_account_id: str,
    sub_account_api_key: str | None = None,
    page: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> list[BrokerSubAccountApiKeyInfo]:
    """List API keys belonging to a sub-account.

    Args:
      sub_account_id: Sub-account identifier.
      sub_account_api_key: Sub-account API key. All of the sub-account's keys if omitted.
      page: Page number, 1-indexed. Default 1.
      size: Records per page. Default 500, max 500.

    References:
      - [Official docs](https://binance-docs.github.io/Brokerage-API/Brokerage_Operation_Endpoints/)
    """
    params: dict = {
      'subAccountId': sub_account_id,
    }
    if sub_account_api_key is not None:
      params['subAccountApiKey'] = sub_account_api_key
    if page is not None:
      params['page'] = page
    if size is not None:
      params['size'] = size
    _Response = list[BrokerSubAccountApiKeyInfo]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/broker/subAccountApi',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def sub_account_api_key_paged(
    self,
    *,
    sub_account_id: str,
    sub_account_api_key: str | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[list[BrokerSubAccountApiKeyInfo]]:
    """Yield successive pages of `sub_account_api_key`.

    Requests `page` from 1 upwards and stops on the first page shorter than `size`, or
    after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.sub_account_api_key(
        sub_account_id=sub_account_id,
        sub_account_api_key=sub_account_api_key,
        size=size,
        page=page,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      if not response or (size is not None and len(response) < size):
        break
      page += 1
