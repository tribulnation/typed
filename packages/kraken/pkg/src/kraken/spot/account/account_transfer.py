"""`spot.account.account_transfer` -- private Spot endpoint."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class AccountTransferResult(TypedDict):
  """Outcome of the account transfer."""

  transfer_id: NotRequired[str]
  """Unique identifier for the transfer."""
  status: NotRequired[Literal['pending', 'complete']]
  """Transfer status."""


validate_account_transfer = validator(AccountTransferResult)


class AccountTransfer(RpcEndpoint):
  """`spot.account.account_transfer`."""

  async def account_transfer(
    self,
    *,
    asset: str,
    amount: str,
    from_: str,
    to: str,
    asset_class: Literal['currency', 'tokenized_asset'] | None = None,
  ) -> AccountTransferResult:
    """Transfer funds to and from the master account and its subaccounts. Must be called using an API key from the master account. Subaccounts are currently only available to institutional clients.

    **API Key Permissions Required:** `Funds permissions - Withdraw`

    Args:
      asset: Asset being transferred (e.g. `XBT`).
      amount: Amount of the asset to transfer.
      from_: Public account ID of the source account (e.g. `ABCD 1234 EFGH 5678`).
      to: Public account ID of the destination account (e.g. `IJKL 0987 MNOP 6543`).
      asset_class: Asset class of the asset being transferred.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/subaccounts/account-transfer)
    """
    data: dict = {
      'asset': asset,
      'amount': amount,
      'from': from_,
      'to': to,
    }
    if asset_class is not None:
      data['asset_class'] = asset_class

    return await self.authed_request(
      '/0/private/AccountTransfer', data, validator=validate_account_transfer
    )
