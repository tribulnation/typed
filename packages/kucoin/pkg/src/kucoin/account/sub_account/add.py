"""`POST /api/v2/sub/user/created` — account.sub_account.add."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class AddSubAccountRequest(TypedDict):
  password: str
  """Login password for the new sub-account: 7-24 characters, must contain letters and numbers, cannot be numbers-only or contain special characters."""
  subName: str
  """Sub-account name: 7-32 characters, at least one letter and one number, no spaces."""
  access: Literal['Spot', 'Futures', 'Margin']
  """Trading permission(s) granted to the sub-account."""
  remarks: NotRequired[str]
  """Optional remarks/notes for the sub-account: 1-24 characters."""


class AddSubAccountResult(TypedDict):
  uid: int
  """Newly created sub-account's numeric user id."""
  subName: str
  """Sub-account name."""
  remarks: str
  """Remarks passed at creation, or empty when none was given."""
  access: str
  """Trading permission(s) granted to the sub-account."""


_Type = AddSubAccountResult
adapter = validator[_Type](_Type)  # type: ignore


class Add(RpcEndpoint):
  """`account.sub_account.add` — mixed into `SubAccount`, the product exposing `account.sub_account.add`."""

  async def add(
    self,
    add_sub_account_request: AddSubAccountRequest,
    *,
    validate: bool | None = None,
  ) -> AddSubAccountResult:
    """Create a new sub-account under the master account. The master API key must carry General permission.

    Args:
      add_sub_account_request: Sub-account creation parameters.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v2/sub/user/created',
      json=add_sub_account_request,
      validator=adapter,
      validate=validate,
    )
