"""`private/list_custody_accounts` — `private/list_custody_accounts`."""

from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from deribit.core import RpcEndpoint


class CustodyAccount(TypedDict):
  currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR']
  """Currency, i.e. `"BTC"`, `"ETH"`, `"USDC"`."""
  name: Literal['copper', 'cobo']
  """Custody provider name."""
  balance: NotRequired[float]
  """Balance available on the custody account."""
  pending_withdrawal_balance: float
  """Pending balance transferred from the trading account to the custody account."""
  auto_deposit: NotRequired[bool]
  """When `true`, all new funds added to the custody balance are automatically transferred to the trading balance."""
  client_id: NotRequired[str]
  """API key `client_id` used to reserve/release funds in the custody platform; requires scope `custody:read_write`."""
  external_id: NotRequired[str]
  """User id in the external custody system."""
  withdrawal_address: NotRequired[str]
  """Address used for withdrawals."""
  withdrawal_address_change: NotRequired[float]
  """UNIX timestamp after which a new withdrawal address will be used for withdrawals."""
  pending_withdrawal_addres: NotRequired[str]
  """New withdrawal address that will be used after `withdrawal_address_change`. (Field name as the venue documents it -- missing a final `s`.)"""
  deposit_address: NotRequired[str]
  """Address that can be used for deposits."""


validate_list_custody_accounts = validator[list[CustodyAccount]](list[CustodyAccount])


class ListCustodyAccounts(RpcEndpoint):
  """`private/list_custody_accounts`."""

  async def list_custody_accounts(
    self,
    *,
    currency: Literal['BTC', 'ETH', 'USDC', 'USDT', 'EURR'],
    validate: bool | None = None,
  ) -> list[CustodyAccount]:
    """Retrieves a list of all custody accounts associated with the authenticated account for a specific currency. Custody accounts are used for clients who require segregated custody of their assets.

    Args:
      currency: The currency symbol.
      validate: Validate the response against the generated schema.

    References:
      - [Deribit API docs](https://docs.deribit.com/api-reference/account-management/private-list_custody_accounts)
    """
    params: dict = {
      'currency': currency,
    }
    return await self.authed_request(
      'private/list_custody_accounts',
      params=params,
      validator=validate_list_custody_accounts,
      validate=validate,
    )
