from dataclasses import dataclass
from datetime import datetime
from typed_core.validation import validator
from typing_extensions import TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class PaymentMethod(TypedDict):
  """A payment method linked to the account, e.g. a bank account or card."""

  id: str
  """Unique identifier for the payment method."""
  type: str
  """The payment method type, e.g. `ACH`."""
  name: str
  """Name for the payment method."""
  currency: str
  """Currency symbol for the payment method."""
  verified: bool
  """The verified status of the payment method."""
  allow_buy: bool
  """Whether or not this payment method can perform buys."""
  allow_sell: bool
  """Whether or not this payment method can perform sells."""
  allow_deposit: bool
  """Whether or not this payment method can perform deposits."""
  allow_withdraw: bool
  """Whether or not this payment method can perform withdrawals."""
  created_at: datetime
  """Time at which this payment method was created, RFC3339."""
  updated_at: datetime | None
  """Time at which this payment method was last updated, RFC3339. `null` when it has never been updated since creation (verified live)."""


class GetPaymentMethodsResponse(TypedDict):
  """The account's linked payment methods."""

  payment_methods: list[PaymentMethod]
  """The account's linked payment methods."""


@dataclass(frozen=True, kw_only=True)
class List(RpcEndpoint):
  """`GET /api/v3/brokerage/payment_methods`."""

  async def list(self) -> GetPaymentMethodsResponse:
    """List the payment methods linked to the calling CDP API Key's Coinbase account.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/payment-methods/list-payment-methods)
    """
    return await self.authed_request(
      'GET',
      '/api/v3/brokerage/payment_methods',
      validator=validator(GetPaymentMethodsResponse),
    )
