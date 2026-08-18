from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class DepositCreditApplyResult(TypedDict):
  """Result of applying deposit credit for an expired address."""

  code: str
  """Response code; `"000000"` on success."""
  message: str
  """Response message; `"success"` on success."""
  data: bool
  """Whether the credit application succeeded."""
  success: bool
  """Whether the request as a whole succeeded."""


class CreditApply(RpcEndpoint):
  """Apply deposit credit for an expired deposit address ("One click arrival"), crediting a deposit that was sent to an address after it stopped being monitored."""

  async def credit_apply(
    self,
    *,
    deposit_id: int | None = None,
    tx_id: str | None = None,
    sub_account_id: int | None = None,
    sub_user_id: int | None = None,
    validate: bool | None = None,
  ) -> DepositCreditApplyResult:
    """Apply deposit credit for an expired deposit address ("One click arrival"), crediting a deposit that was sent to an address after it stopped being monitored.

    Args:
      deposit_id: Deposit record id. Takes priority over `txId` when both are supplied.
      tx_id: Deposit transaction id. Used when `depositId` is not supplied.
      sub_account_id: Sub-account id of a Cloud user, for a deposit credited to a sub-account.
      sub_user_id: Sub-user id of the parent user, for a deposit credited to a sub-account.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#one-click-arrival-deposit-apply)
    """
    params = {}
    if deposit_id is not None:
      params['depositId'] = deposit_id
    if tx_id is not None:
      params['txId'] = tx_id
    if sub_account_id is not None:
      params['subAccountId'] = sub_account_id
    if sub_user_id is not None:
      params['subUserId'] = sub_user_id
    _Response = DepositCreditApplyResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/capital/deposit/credit-apply',
      params=params,
      validator=_validator,
      validate=validate,
    )
