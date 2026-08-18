from decimal import Decimal
from datetime import datetime
from typing_extensions import Any, Literal, NotRequired, TypedDict
from bit2me.types import AmountCurrencyObject, Phone, Rate, TransactionSubsFeeTypeParam
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class BankAccount(TypedDict):
  bankAccount: str
  swiftBic: NotRequired[str]
  country: str
  receiverName: NotRequired[str]
  bankName: NotRequired[str]
  bankAddress: NotRequired[str]
  bankCode: NotRequired[str]
  bankBranch: NotRequired[str]


class Creditcard(TypedDict):
  cardId: str


class Fixed(TypedDict):
  """Fixed component of the Teller fee, charged regardless of the transaction amount."""

  amount: Decimal
  """Fixed fee amount charged, in `currency`."""
  currency: str
  """Valid currency symbol"""


class Flip(TypedDict):
  """Flip fee"""

  percentage: Decimal
  """Conversion fee rate applied, as a percentage of the converted amount."""
  amount: Decimal
  """Conversion fee amount charged, in `currency`."""
  currency: str
  """Valid currency symbol"""


class Network(TypedDict):
  """Network fee"""

  amount: Decimal
  """Network fee amount charged, in `currency`."""
  currency: str
  """Currency the network fee is charged in."""


class UserAmount(TypedDict):
  """The transaction amount converted to the user's currency (`userCurrency` on the request, EUR by default)."""

  currency: str
  """Valid currency symbol"""
  amount: Decimal
  """Amount in the user's currency."""


class Variable(TypedDict):
  """Variable component of the Teller fee, proportional to the transaction amount."""

  percentage: Decimal
  """Variable fee rate applied, as a percentage of the transaction amount."""
  amount: Decimal
  """Variable fee amount charged, in `currency`."""
  currency: str
  """Valid currency symbol"""


class Destination(TypedDict):
  address: NotRequired[str]
  pocket: NotRequired[str]
  bankAccount: NotRequired[BankAccount]
  email: NotRequired[str]
  phone: NotRequired[Phone]
  alias: NotRequired[str]
  network: NotRequired[str]
  """The destination address network"""


class Origin(TypedDict):
  creditcard: NotRequired[Creditcard]


class Teller(TypedDict):
  """Fee charged by Teller, Bit2Me's card payment processor, present only when the transaction is funded by a credit or debit card purchase."""

  fixed: Fixed
  variable: Variable


class Fee(TypedDict):
  """Different fees for the transaction"""

  network: NotRequired[Network]
  flip: NotRequired[Flip]
  teller: NotRequired[Teller]


class WalletTransactionProformaRequest(TypedDict):
  operation: NotRequired[
    Literal[
      'purchase',
      'withdrawal-trading',
      'deposit-trading',
      'social-payment',
      'launchpad-purchase',
      'buy',
      'sell',
    ]
  ]
  """This property is not necessary for other operation types"""
  pair: NotRequired[str]
  pocket: NotRequired[str]
  amount: str
  currency: str
  type: NotRequired[TransactionSubsFeeTypeParam]
  concept: NotRequired[str]
  note: NotRequired[str]
  receiverName: NotRequired[str]
  origin: NotRequired[Origin]
  destination: NotRequired[Destination]
  userCurrency: NotRequired[str]
  """The user's currency (used to show a rate from it to Euro)"""
  queryParams: NotRequired[dict[str, Any]]
  """Used for some cryptos that need extra parameters to do blockchain sendings. For example, memo in XRP."""


class WalletTransactionProformaResponse(TypedDict):
  id: str
  """Id of this proforma transaction. Pass it as `proforma` to `POST /v1/wallet/transaction` to execute it before it expires."""
  expirationTime: datetime
  """When this proforma expires (ISO 8601). It must be executed via `POST /v1/wallet/transaction` before this time, or previewed again."""
  origin: AmountCurrencyObject
  destination: AmountCurrencyObject
  fee: NotRequired[Fee]
  flip: NotRequired[Rate]
  userRate: NotRequired[Rate]
  userAmount: NotRequired[UserAmount]


validate_response = validator(WalletTransactionProformaResponse)


class Preview(RpcEndpoint):
  async def preview(
    self,
    wallet_transaction_proforma_request: WalletTransactionProformaRequest,
    *,
    validate: bool | None = None,
  ) -> WalletTransactionProformaResponse:
    """Create a new proforma transaction, including its expiration time.

    - If `type` is not specified, `REA` is used by default.
    - `destination` only accepts one field. Use `destination.address` for a cryptocurrency address or `destination.pocket` for the destination pocket ID.
    - The user's email must be validated before calling this endpoint.
    - For peer-to-peer transactions, a sell operation must be made on the source pocket and a buy operation must be made on the destination pocket.
    - All blockchain withdrawals must include Travel Rule information before they can be processed. See `POST /v1/blockchain-manager/travel-rule-order/{orderId}`.

    Args:
      wallet_transaction_proforma_request: The operation to preview: amount and currency to move, plus the origin and/or destination it moves between.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/wallet/POST/v1/wallet/transaction/proforma)
    """
    return await self.authed_request(
      'POST',
      '/v1/wallet/transaction/proforma',
      json=wallet_transaction_proforma_request,
      validator=validate_response,
      validate=validate,
    )
