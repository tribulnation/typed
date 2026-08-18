from decimal import Decimal
from datetime import datetime
from typing_extensions import Literal, NotRequired, TypedDict
from bit2me.types import AmountCurrencyObject, Rate, TransactionSubsFeeTypeParam
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class Flip(TypedDict):
  """Fee charged for converting between currencies, present only when the transaction includes a currency conversion (an instant trade)."""

  percentage: Decimal
  """Conversion fee rate applied, as a percentage of the converted amount."""
  amount: Decimal
  """Conversion fee amount charged, in `currency`."""
  currency: str
  """Valid currency symbol"""


class Teller(TypedDict):
  """Fee charged by Teller, Bit2Me's card payment processor, present only when the transaction was funded by a credit or debit card purchase."""

  id: NotRequired[str]
  """Teller orderId"""
  feeCurrency: NotRequired[str]
  """Currency of the fees"""
  fixedFee: NotRequired[str]
  """Fixed fee"""
  variableFee: NotRequired[str]
  """Variable fee"""
  variableFeePercentage: NotRequired[str]
  """Variable fee percentage"""


class Transaction(TypedDict):
  """Network transaction"""

  hash: str
  """Network transaction hash"""
  confirmedAt: NotRequired[datetime]
  """When the transaction was confirmed (ISO 8601)."""
  confirmationCount: NotRequired[float]
  """The number of confirmations the transaction has."""


DestinationKeywords = TypedDict(
  'DestinationKeywords',
  {'class': Literal['pocket', 'network', 'blockchain', 'b2m', 'bankAccount']},
)
"""
  - `class`:   Type of the destination:
     - pocket: destination is another pocket
     - network: destination is an cryptocurrency address
     - b2m: destination is another Bit2Me user
     - bankAccount: destination is a bank account

"""


class Destination(DestinationKeywords):
  """Transaction destination"""

  currency: str
  """The currency of the destination"""
  amount: Decimal
  """The total amount of "money" that the destination receives"""
  pocketName: NotRequired[str | None]
  """The destination pocket name"""
  pocketId: NotRequired[str | None]
  """The destination pocket ID"""
  address: NotRequired[str | None]
  """The destination address"""
  addressNetwork: NotRequired[str | None]
  """The destination address network"""
  addressInBlacklist: NotRequired[bool | None]
  """Indicates if destination address is in blacklist"""
  addressTag: NotRequired[str | None]
  """Destination address tag or memo, for networks that require one (e.g. XRP, XLM) to route funds to the recipient's account; null when the network or destination doesn't use one."""
  rate: NotRequired[Rate]


class Fee(TypedDict):
  """Different fees for the transaction:
  network: only present when type is "withdrawal"
  flip: only present when the transaction has a currency convertion (instant)"""

  network: NotRequired[AmountCurrencyObject]
  flip: NotRequired[Flip]
  teller: NotRequired[Teller]


OriginKeywords = TypedDict(
  'OriginKeywords',
  {'class': Literal['pocket', 'network', 'b2m', 'card', 'bank transfer', 'trading']},
)
"""
  - `class`:   Type of the origin:
     - pocket: origin is another pocket
     - network: origin is a cryptocurrency address
     - b2m: origin is another Bit2Me user
     - card: origin is a credit or debit card
     - bank transfer: origin is a bank transfer
     - trading: origin is trading balance

"""


class Origin(OriginKeywords):
  """Transaction origin"""

  currency: str
  """The origin currency"""
  amount: Decimal
  """The total amount of "money" that is taken from origin."""
  pocketName: NotRequired[str | None]
  """The origin pocket name"""
  pocketId: NotRequired[str | None]
  """The origin pocket ID"""
  rate: NotRequired[Rate]


class WalletTransactionDetailResponse(TypedDict):
  date: datetime
  """When the transaction was created (ISO 8601)"""
  type: Literal['deposit', 'withdrawal', 'transfer']
  """Type of the transaction"""
  concept: NotRequired[str | None]
  """The concept of the transaction"""
  note: NotRequired[str | None]
  """Personal note of the user"""
  origin: Origin
  destination: Destination
  transaction: NotRequired[Transaction]
  fee: NotRequired[Fee]
  flip: NotRequired[Rate]
  substractFeeType: NotRequired[TransactionSubsFeeTypeParam | None]
  """Whether the transaction amount is what the receiver gets (REA) or what is deducted from the sender's balance (SEA). Null when the distinction doesn't apply, e.g. deposits."""


validate_response = validator(WalletTransactionDetailResponse)


class Get(RpcEndpoint):
  async def get(
    self,
    id: str,
    *,
    user_currency: str | None = None,
    validate: bool | None = None,
  ) -> WalletTransactionDetailResponse:
    """Get the details of a transaction

    Args:
      id: The transaction id (returned by GET /v1/transaction)
      user_currency: The user's currency (used to show a rate from it to Euro)
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/wallet/GET/v1/wallet/transaction/{id})
    """
    params = {'userCurrency': user_currency} if user_currency is not None else None
    return await self.authed_request(
      'GET',
      f'/v1/wallet/transaction/{id}',
      params=params,
      validator=validate_response,
      validate=validate,
    )
