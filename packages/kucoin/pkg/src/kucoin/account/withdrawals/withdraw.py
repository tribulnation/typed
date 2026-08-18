"""`POST /api/v3/withdrawals` — account.withdrawals.withdraw."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class WithdrawResult(TypedDict):
  withdrawalId: str
  """Unique id assigned to the new withdrawal."""


class WithdrawV3request(TypedDict):
  currency: str
  """Currency to withdraw, e.g. `BTC`, `ETH`, `USDT`."""
  toAddress: str
  """Withdrawal destination: an on-chain address, internal KuCoin UID, email, or phone number, depending on `withdrawType`."""
  amount: str
  """Withdrawal amount, a positive number that is a multiple of the currency's amount precision."""
  withdrawType: Literal['ADDRESS', 'UID', 'MAIL', 'PHONE']
  """How `toAddress` is interpreted. Withdrawing by UID/email/phone is additionally rate-limited to 3 requests/10s and 50/24h."""
  chain: NotRequired[str]
  """Chain id of the currency, recommended for any multi-chain currency rather than relying on the account default (queryable via the currency detail endpoint). Defaults to `eth`."""
  memo: NotRequired[str]
  """Address remark/tag. Required by some destinations (e.g. withdrawing to another exchange) -- omitting a required memo can cause the deposit to be lost on the receiving side."""
  isInner: NotRequired[bool]
  """Whether this is an internal (KuCoin-to-KuCoin) withdrawal."""
  remark: NotRequired[str]
  """Free-text remark for this withdrawal."""
  feeDeductType: NotRequired[Literal['INTERNAL', 'EXTERNAL']]
  """Which account the withdrawal fee is deducted from. If omitted, the fee is deducted from the main account when its balance covers it, otherwise from the withdrawal amount itself."""


_Type = WithdrawResult
adapter = validator[_Type](_Type)  # type: ignore


class Withdraw(RpcEndpoint):
  """`account.withdrawals.withdraw` — mixed into `Withdrawals`, the product exposing `account.withdrawals.withdraw`."""

  async def withdraw(
    self,
    withdraw_v3request: WithdrawV3request,
    *,
    validate: bool | None = None,
  ) -> WithdrawResult:
    """Withdraw the specified currency to an external address, another KuCoin account (internal transfer), a UID, an email, or a phone number.

    Args:
      withdraw_v3request: Withdrawal parameters.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v3/withdrawals',
      json=withdraw_v3request,
      validator=adapter,
      validate=validate,
    )
