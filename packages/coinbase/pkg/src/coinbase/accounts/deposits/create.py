from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint
from coinbase.types import V2transfer


class DepositFundsResponse(TypedDict):
  """Wrapper around the created deposit transfer."""

  transfer: V2transfer


@dataclass(frozen=True, kw_only=True)
class Create(RpcEndpoint):
  """`POST /v2/accounts/{account_id}/deposits`."""

  async def create(
    self,
    account_id: str,
    *,
    amount: str,
    currency: str,
    payment_method: str,
    commit: bool | None = None,
  ) -> DepositFundsResponse:
    """Deposit a user-defined amount of funds to a fiat account from a linked payment method. Pass `commit: false` to create the deposit without executing it, to be completed later with Commit Deposit.

    Args:
      account_id: The fiat account to deposit into.
      amount: Deposit amount.
      currency: Currency for `amount`.
      payment_method: Id of the payment method to deposit from. See `accounts.deposits.list` -- payment methods themselves are listed via `advanced_trade.payment_methods.list`.
      commit: If false, this deposit is not immediately completed; complete it later with Commit Deposit.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/coinbase-app/transfer-apis/deposit-fiat)
    """
    body: dict = {
      'amount': amount,
      'currency': currency,
      'payment_method': payment_method,
    }
    if commit is not None:
      body['commit'] = commit
    return await self.authed_request(
      'POST',
      f'/v2/accounts/{account_id}/deposits',
      json=body,
      validator=validator(DepositFundsResponse),
    )
