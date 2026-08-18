"""`private/get_block_rfq_user_info` — `private/get_block_rfq_user_info`."""

from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class BlockRfqParentIdentity(TypedDict):
  """Group-level alias (main account + subaccounts), when the group has one."""

  identity: NotRequired[str]
  """Group-level alias identifying the account group as a whole."""
  is_maker: NotRequired[bool]
  """Whether the parent identity has maker scope."""


class BlockRfqUserIdentity(TypedDict):
  """Identity/rating info for one account (main or subaccount)."""

  user_id: int
  """Unique user identifier."""
  taker_rating: NotRequired[float]
  """Taker rating for this account, when available."""
  identity: NotRequired[str]
  """Alias identifying this account individually, when available."""
  is_maker: NotRequired[bool]
  """Whether this account has maker scope."""


class BlockRfqUserInfo(TypedDict):
  """Block RFQ identity/rating info for the account group and its individual accounts."""

  parent: NotRequired[BlockRfqParentIdentity]
  users: NotRequired[list[BlockRfqUserIdentity]]
  """Per-account identity/rating entries (main account and subaccounts)."""


validate_get_block_rfq_user_info = validator[BlockRfqUserInfo](BlockRfqUserInfo)


class GetBlockRfqUserInfo(RpcEndpoint):
  """`private/get_block_rfq_user_info`."""

  async def get_block_rfq_user_info(
    self,
    *,
    validate: bool | None = None,
  ) -> BlockRfqUserInfo:
    """Returns identity and rating information for the requesting account and its subaccounts. Includes both group-level and individual user-level alias data, where available -- useful for understanding one's own Block RFQ maker identity and rating.

    Scope: `block_rfq:read`.

    Args:
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/block-rfq/private-get_block_rfq_user_info)
    """
    return await self.authed_request(
      'private/get_block_rfq_user_info',
      validator=validate_get_block_rfq_user_info,
      validate=validate,
    )
