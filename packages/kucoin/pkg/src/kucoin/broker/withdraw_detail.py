"""`GET /api/v3/broker/nd/withdraw/detail` — Get Withdraw Detail."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class BrokerWithdrawDetail(TypedDict):
  """Detail of one sub-account withdrawal."""

  id: str
  """Withdrawal id."""
  chain: str
  """Chain id of the currency."""
  walletTxId: str
  """Wallet transaction id."""
  uid: int
  """Withdrawing sub-account's UID."""
  updatedAt: int
  """Record last-update time, Unix milliseconds."""
  amount: str
  """Withdrawal amount."""
  memo: str
  """Address memo/tag; empty string if none."""
  fee: str
  """Fee charged for the withdrawal."""
  address: str
  """Destination withdrawal address."""
  remark: str
  """Free-text remark; empty string if none."""
  isInner: bool
  """Whether this was an internal (KuCoin-to-KuCoin) withdrawal rather than on-chain."""
  currency: str
  """Currency withdrawn."""
  status: Literal['PROCESSING', 'WALLET_PROCESSING', 'REVIEW', 'SUCCESS', 'FAILURE']
  """Withdrawal status."""
  createdAt: int
  """Record creation time, Unix milliseconds."""


_Type = BrokerWithdrawDetail
adapter = validator[_Type](_Type)  # type: ignore


class WithdrawDetail(RpcEndpoint):
  """`Get Withdraw Detail` — mixed into `Broker`, the product exposing `broker.withdraw_detail`."""

  async def withdraw_detail(
    self,
    *,
    withdrawal_id: str,
    validate: bool | None = None,
  ) -> BrokerWithdrawDetail:
    """Get the detail of one withdrawal from an Exchange (ND) Broker sub-account, by withdrawal id. Excludes the broker's own main account.

    Args:
      withdrawal_id: Withdrawal id.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'withdrawalId': withdrawal_id,
    }
    return await self.authed_request(
      'GET',
      '/api/v3/broker/nd/withdraw/detail',
      params=params,
      validator=adapter,
      validate=validate,
    )
