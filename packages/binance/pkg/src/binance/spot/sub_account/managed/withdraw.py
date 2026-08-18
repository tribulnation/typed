from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class ManagedSubAccountWithdrawResult(TypedDict):
  """The executed withdrawal."""

  tranId: NotRequired[int]
  """Transfer id."""


class Withdraw(RpcEndpoint):
  """Withdraw an asset from a Managed Sub-Account back to the investor master account, for the investor master account."""

  async def withdraw(
    self,
    *,
    from_email: str,
    asset: str,
    amount: float,
    transfer_date: int | None = None,
    validate: bool | None = None,
  ) -> ManagedSubAccountWithdrawResult:
    """Withdraw an asset from a Managed Sub-Account back to the investor master account, for the investor master account.

    Args:
      from_email: Managed Sub-Account email to withdraw from.
      asset: Asset to withdraw.
      amount: Amount to withdraw.
      transfer_date: Date (UTC) the withdrawal should take effect. Omit to withdraw immediately.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-sub-account/api/rest-api/managed-sub-account#withdrawl-assets-from-the-managed-sub-account)
    """
    params: dict = {
      'fromEmail': from_email,
      'asset': asset,
      'amount': amount,
    }
    if transfer_date is not None:
      params['transferDate'] = transfer_date
    _Response = ManagedSubAccountWithdrawResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/managed-subaccount/withdraw',
      params=params,
      validator=_validator,
      validate=validate,
    )
