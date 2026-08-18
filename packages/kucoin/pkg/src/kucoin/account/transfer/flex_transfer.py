"""`POST /api/v3/accounts/universal-transfer` — Flex Transfer."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class FlexTransferRequest(TypedDict):
  clientOid: str
  """Client-assigned unique idempotency key, e.g. a UUID, max 128 bits."""
  currency: str
  """Currency to transfer, e.g. `USDT`, `BTC`."""
  amount: str
  """Transfer amount; must be a positive integer multiple of the currency's precision."""
  fromUserId: NotRequired[str]
  """Source user ID. Required for `SUB_TO_PARENT`; optional for `INTERNAL`."""
  fromAccountType: Literal[
    'MAIN',
    'TRADE',
    'CONTRACT',
    'MARGIN',
    'ISOLATED',
    'MARGIN_V2',
    'ISOLATED_V2',
    'OPTION',
  ]
  """Source account type."""
  fromAccountTag: NotRequired[str]
  """Trading pair symbol, required when `fromAccountType` is `ISOLATED` or `ISOLATED_V2`, e.g. `BTC-USDT`."""
  type: Literal['INTERNAL', 'PARENT_TO_SUB', 'SUB_TO_PARENT']
  """Transfer scenario."""
  toUserId: NotRequired[str]
  """Destination user ID. Required for `PARENT_TO_SUB`; optional for `INTERNAL`."""
  toAccountType: Literal[
    'MAIN',
    'TRADE',
    'CONTRACT',
    'MARGIN',
    'ISOLATED',
    'MARGIN_V2',
    'ISOLATED_V2',
    'OPTION',
  ]
  """Destination account type."""
  toAccountTag: NotRequired[str]
  """Trading pair symbol, required when `toAccountType` is `ISOLATED` or `ISOLATED_V2`, e.g. `BTC-USDT`."""


class FlexTransferResult(TypedDict):
  orderId: str
  """Transfer order ID."""


_Type = FlexTransferResult
adapter = validator[_Type](_Type)  # type: ignore


class FlexTransfer(RpcEndpoint):
  """`Flex Transfer` — mixed into `Transfer`, the product exposing `account.transfer.flex_transfer`."""

  async def flex_transfer(
    self,
    flex_transfer_request: FlexTransferRequest,
    *,
    validate: bool | None = None,
  ) -> FlexTransferResult:
    """Move funds between account types on one user, or between a master account and one of its sub-accounts. One endpoint covers three scenarios (`type`): INTERNAL (within one account, between account types), PARENT_TO_SUB (master to a named sub-account) and SUB_TO_PARENT (sub-account to the master account).

    Args:
      flex_transfer_request: Transfer parameters.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v3/accounts/universal-transfer',
      json=flex_transfer_request,
      validator=adapter,
      validate=validate,
    )
