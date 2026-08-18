"""`DELETE /api/v1/sub/api-key` — account.sub_account_api.delete."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class DeleteSubAccountApiResult(TypedDict):
  subName: str
  """Sub-account name the deleted key belonged to."""
  apiKey: str
  """The deleted API key's identifier."""


_Type = DeleteSubAccountApiResult
adapter = validator[_Type](_Type)  # type: ignore


class Delete(RpcEndpoint):
  """`account.sub_account_api.delete` — mixed into `SubAccountApi`, the product exposing `account.sub_account_api.delete`."""

  async def delete(
    self,
    *,
    api_key: str,
    sub_name: str,
    passphrase: str,
    validate: bool | None = None,
  ) -> DeleteSubAccountApiResult:
    """Delete an existing sub-account API key. The key's passphrase must be supplied to authorize the deletion.

    Args:
      api_key: API key identifier to delete.
      sub_name: Sub-account name the key belongs to.
      passphrase: The key's existing API passphrase, required to authorize the deletion.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'apiKey': api_key,
      'subName': sub_name,
      'passphrase': passphrase,
    }
    return await self.authed_request(
      'DELETE',
      '/api/v1/sub/api-key',
      params=params,
      validator=adapter,
      validate=validate,
    )
