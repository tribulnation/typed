"""`POST /api/v1/broker/nd/account/update-apikey` — Modify sub-account API."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class BrokerSubAccountApiKeyModified(TypedDict):
  """A broker sub-account API key after modification."""

  uid: str
  """Sub-account UID."""
  label: str
  """API key remarks."""
  apiKey: str
  """The API key."""
  apiVersion: int
  """API key version."""
  permissions: list[str]
  """Permission group list assigned to the key."""
  ipWhitelist: list[str]
  """IP whitelist assigned to the key."""
  createdAt: int
  """Creation time, Unix milliseconds."""


class ModifySubAccountApiRequest(TypedDict):
  uid: str
  """Sub-account UID owning the key."""
  apiKey: str
  """API key to modify."""
  ipWhitelist: list[str]
  """New IP whitelist, up to 20 entries."""
  permissions: list[Literal['general', 'spot', 'futures']]
  """New permission group list -- only `general`, `spot` and `futures` may be set here."""
  label: str
  """New API key remarks, 4-32 characters."""


_Type = BrokerSubAccountApiKeyModified
adapter = validator[_Type](_Type)  # type: ignore


class SubAccountApiModify(RpcEndpoint):
  """`Modify sub-account API` — mixed into `Broker`, the product exposing `broker.sub_account_api_modify`."""

  async def sub_account_api_modify(
    self,
    modify_sub_account_api_request: ModifySubAccountApiRequest,
    *,
    validate: bool | None = None,
  ) -> BrokerSubAccountApiKeyModified:
    """Update the IP whitelist, permission set and/or label of an existing Exchange (ND) Broker sub-account API key.

    Args:
      modify_sub_account_api_request: The key to modify, and its new IP whitelist, permissions and label.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/broker/nd/account/update-apikey',
      json=modify_sub_account_api_request,
      validator=adapter,
      validate=validate,
    )
