from typing_extensions import Any, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class FiatWithdrawAccountInfo(TypedDict):
  """Destination bank account for a fiat withdrawal."""

  accountNumber: str
  """Destination bank account number. In Argentina, this is the CBU/CVU; in Mexico, the CLABE."""
  agency: NotRequired[str]
  """Bank agency code. If it contains a hyphen (e.g. `123-4`), enter `123` only."""
  bankCodeForPix: NotRequired[str]
  """Bank code used for PIX routing."""
  accountType: NotRequired[str]
  """Account type, e.g. `current` (checking account) or `saving` (savings account)."""


class FiatWithdrawOrder(TypedDict):
  """Identifier of the created withdrawal order."""

  orderId: NotRequired[str]
  """Identifier of the created withdrawal order."""


class FiatWithdrawResult(TypedDict):
  """Result of submitting a fiat withdrawal request."""

  code: NotRequired[str]
  """Response code. "000000" indicates success."""
  message: NotRequired[str]
  """Response message."""
  data: NotRequired[FiatWithdrawOrder]


class Withdraw(RpcEndpoint):
  """Submit a fiat withdrawal request. In this version, BRL, ARS and MXN withdrawal via bank_transfer are supported. After calling this, poll spot.fiat.order_detail with the returned order number until the withdrawal succeeds. Requires the account to have completed KYC/KYB and activated fiat service on binance.com."""

  async def withdraw(
    self,
    *,
    currency: str,
    api_payment_method: Literal['bank_transfer'],
    amount: int,
    account_info: FiatWithdrawAccountInfo,
    ext: dict[str, Any] | None = None,
    validate: bool | None = None,
  ) -> FiatWithdrawResult:
    """Submit a fiat withdrawal request. In this version, BRL, ARS and MXN withdrawal via bank_transfer are supported. After calling this, poll spot.fiat.order_detail with the returned order number until the withdrawal succeeds. Requires the account to have completed KYC/KYB and activated fiat service on binance.com.

    Args:
      currency: Fiat currency to withdraw, e.g. BRL, ARS, MXN.
      api_payment_method: Payment method.
      amount: Withdraw amount.
      account_info: Destination bank account for the withdrawal.
      ext: Additional payment-method-specific extension fields.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-fiat/api/rest-api/~#fiat-withdraw)
    """
    params: dict = {
      'currency': currency,
      'apiPaymentMethod': api_payment_method,
      'amount': amount,
      'accountInfo': account_info,
    }
    if ext is not None:
      params['ext'] = ext
    _Response = FiatWithdrawResult
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v2/fiat/withdraw',
      params=params,
      validator=_validator,
      validate=validate,
    )
