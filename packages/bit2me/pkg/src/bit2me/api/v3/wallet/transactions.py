from decimal import Decimal
from datetime import datetime
from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from bit2me.types import TransactionSubsFeeTypeParam
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator


class CursorPageInfo(TypedDict):
  """Cursor pagination state for this page."""

  hasNextPage: bool
  """Whether a further page exists after this one."""
  endCursor: str | None
  """Cursor to pass as `cursor` to fetch the next page; `null` once `hasNextPage` is `false`."""


class DenominationRatePair(TypedDict):
  """Currency pair a rate is quoted for."""

  base: NotRequired[str]
  """Base currency of the pair."""
  quote: NotRequired[str]
  """Quote currency of the pair."""


class TransactionBenefit(TypedDict):
  """Loyalty/rewards benefit earned on this transaction, when applicable."""

  tier: NotRequired[int]
  """Benefit tier applied."""
  levelId: NotRequired[str]
  """Identifier of the benefit level."""
  quantity: NotRequired[Decimal]
  """Quantity of benefit units earned."""
  percentage: NotRequired[int]
  """Percentage of the benefit applied."""
  currency: NotRequired[str]
  """Currency the benefit `amount` is denominated in."""
  amount: NotRequired[Decimal]
  """Amount of benefit earned, in `currency`."""


class TransactionCompanyRatePair(TypedDict):
  """Currency pair a rate is quoted for."""

  base: NotRequired[str]
  """Base currency of the pair."""
  quote: NotRequired[str]
  """Quote currency of the pair."""


class TransactionDestinationConverted(TypedDict):
  """This side's amount converted into another reference currency."""

  amount: NotRequired[Decimal]
  """Converted amount, in `currency`."""
  amountAfterFees: NotRequired[Decimal]
  """Converted amount after fees, in `currency`."""
  currency: NotRequired[str]
  """Currency the converted amount is denominated in."""


class TransactionDestinationPhone(TypedDict):
  """Phone number of the counterparty, when this side is another Bit2Me user identified by phone."""

  number: NotRequired[str]
  """Phone number, without the country code."""
  countryCode: NotRequired[str]
  """Country calling code of `number`."""


class TransactionDestinationRatePair(TypedDict):
  """Currency pair a rate is quoted for."""

  base: NotRequired[str]
  """Base currency of the pair."""
  quote: NotRequired[str]
  """Quote currency of the pair."""


class TransactionDestinationUserAmount(TypedDict):
  """This side's amount expressed in the user's preferred display currency."""

  currency: NotRequired[str]
  """Currency `value` is denominated in."""
  value: NotRequired[Decimal]
  """Amount in `currency`."""


class TransactionFlipFee(TypedDict):
  """Fee charged for an instant currency conversion."""

  percentage: NotRequired[Decimal]
  """Conversion fee, as a percentage of the amount converted."""
  amount: NotRequired[Decimal]
  """Conversion fee amount, in `currency`."""
  currency: NotRequired[str]
  """Currency the conversion fee is denominated in."""


class TransactionFlipRatePair(TypedDict):
  """Currency pair a rate is quoted for."""

  base: NotRequired[str]
  """Base currency of the pair."""
  quote: NotRequired[str]
  """Quote currency of the pair."""


class TransactionNetworkDetails(TypedDict):
  """On-chain transaction details, present when the transaction involves a blockchain movement."""

  hash: NotRequired[str]
  """Blockchain transaction hash."""
  confirmedAt: NotRequired[datetime]
  """When the transaction was confirmed on-chain (ISO 8601)."""
  confirmationCount: NotRequired[int]
  """Number of blockchain confirmations received."""


class TransactionNetworkFee(TypedDict):
  """Network (blockchain) fee charged for the transaction."""

  amount: NotRequired[Decimal]
  """Network fee amount, in `currency`."""
  currency: NotRequired[str]
  """Currency the network fee is denominated in."""


class TransactionOriginConverted(TypedDict):
  """This side's amount converted into another reference currency."""

  amount: NotRequired[Decimal]
  """Converted amount, in `currency`."""
  amountAfterFees: NotRequired[Decimal]
  """Converted amount after fees, in `currency`."""
  currency: NotRequired[str]
  """Currency the converted amount is denominated in."""


class TransactionOriginPhone(TypedDict):
  """Phone number of the counterparty, when this side is another Bit2Me user identified by phone."""

  number: NotRequired[str]
  """Phone number, without the country code."""
  countryCode: NotRequired[str]
  """Country calling code of `number`."""


class TransactionOriginRatePair(TypedDict):
  """Currency pair a rate is quoted for."""

  base: NotRequired[str]
  """Base currency of the pair."""
  quote: NotRequired[str]
  """Quote currency of the pair."""


class TransactionOriginUserAmount(TypedDict):
  """This side's amount expressed in the user's preferred display currency."""

  currency: NotRequired[str]
  """Currency `value` is denominated in."""
  value: NotRequired[Decimal]
  """Amount in `currency`."""


class TransactionTellerFixedFee(TypedDict):
  """Fixed component of the teller fee."""

  amount: NotRequired[Decimal]
  """Fixed fee amount, in `currency`."""
  currency: NotRequired[str]
  """Currency the fixed fee is denominated in."""


class TransactionTellerVariableFee(TypedDict):
  """Variable component of the teller fee."""

  percentage: NotRequired[str]
  """Variable fee, as a percentage of the amount."""
  amount: NotRequired[Decimal]
  """Variable fee amount, in `currency`."""
  currency: NotRequired[str]
  """Currency the variable fee is denominated in."""


class TransactionUserAmount(TypedDict):
  """Transaction amount expressed in the user's preferred display currency."""

  currency: NotRequired[str]
  """Currency `amount` is denominated in."""
  amount: NotRequired[Decimal]
  """Amount in `currency`."""


class TransactionUserExchangeRatePair(TypedDict):
  """Currency pair a rate is quoted for."""

  base: NotRequired[str]
  """Base currency of the pair."""
  quote: NotRequired[str]
  """Quote currency of the pair."""


class DenominationRate(TypedDict):
  """Exchange rate quoted between two currencies."""

  value: NotRequired[Decimal]
  """Exchange rate value from `pair.base` to `pair.quote`."""
  extraDecimals: NotRequired[str]
  """Number of extra decimal digits of precision carried by `value` beyond its default display formatting."""
  pair: NotRequired[DenominationRatePair]


class TransactionCompanyRate(TypedDict):
  """Exchange rate quoted between two currencies."""

  value: NotRequired[Decimal]
  """Exchange rate value from `pair.base` to `pair.quote`."""
  extraDecimals: NotRequired[str]
  """Number of extra decimal digits of precision carried by `value` beyond its default display formatting."""
  pair: NotRequired[TransactionCompanyRatePair]


class TransactionDestinationRate(TypedDict):
  """Exchange rate quoted between two currencies."""

  value: NotRequired[Decimal]
  """Exchange rate value from `pair.base` to `pair.quote`."""
  extraDecimals: NotRequired[str]
  """Number of extra decimal digits of precision carried by `value` beyond its default display formatting."""
  pair: NotRequired[TransactionDestinationRatePair]


class TransactionFlipRate(TypedDict):
  """Exchange rate quoted between two currencies."""

  value: NotRequired[Decimal]
  """Exchange rate value from `pair.base` to `pair.quote`."""
  extraDecimals: NotRequired[str]
  """Number of extra decimal digits of precision carried by `value` beyond its default display formatting."""
  pair: NotRequired[TransactionFlipRatePair]


class TransactionOriginRate(TypedDict):
  """Exchange rate quoted between two currencies."""

  value: NotRequired[Decimal]
  """Exchange rate value from `pair.base` to `pair.quote`."""
  extraDecimals: NotRequired[str]
  """Number of extra decimal digits of precision carried by `value` beyond its default display formatting."""
  pair: NotRequired[TransactionOriginRatePair]


class TransactionTellerFee(TypedDict):
  """Teller/card-related fee for the transaction."""

  fixed: NotRequired[TransactionTellerFixedFee]
  variable: NotRequired[TransactionTellerVariableFee]
  id: NotRequired[str]
  """Teller order identifier."""
  feeCurrency: NotRequired[str]
  """Currency the teller fees are denominated in."""
  fixedFee: NotRequired[Decimal]
  """Fixed teller fee amount."""
  variableFee: NotRequired[Decimal]
  """Variable teller fee amount."""
  variableFeePercentage: NotRequired[str]
  """Variable teller fee, as a percentage."""


class TransactionUserExchangeRate(TypedDict):
  """Exchange rate quoted between two currencies."""

  value: NotRequired[Decimal]
  """Exchange rate value from `pair.base` to `pair.quote`."""
  extraDecimals: NotRequired[str]
  """Number of extra decimal digits of precision carried by `value` beyond its default display formatting."""
  pair: NotRequired[TransactionUserExchangeRatePair]


class TransactionCompanyDestination(TypedDict):
  """The company's side of the transaction."""

  currency: NotRequired[str]
  """Currency `amount` is denominated in."""
  amount: NotRequired[Decimal]
  """Amount in `currency`."""
  rate: NotRequired[TransactionCompanyRate]


class TransactionDenomination(TypedDict):
  """The transaction amount and currency the user transacted in, together with its exchange rate. Absent for purely internal pocket-to-pocket or pocket-to-trading transfers."""

  amount: NotRequired[Decimal]
  """Amount of the transaction in `currency`."""
  currency: NotRequired[str]
  """Currency `amount` is denominated in."""
  rate: NotRequired[DenominationRate]


TransactionDestinationKeywords = TypedDict(
  'TransactionDestinationKeywords', {'class': NotRequired[str]}
)
"""
- `class`: Kind of counterparty this side of the transaction represents, e.g. `pocket`, `blockchain`, `trading`, `earn` (observed values; not declared as a closed set, see the endpoint `notes`).
"""


class TransactionDestination(TransactionDestinationKeywords):
  """The destination side of the transaction: a pocket, a blockchain address, a bank account, a card, or another Bit2Me user."""

  currency: NotRequired[str]
  """Currency `amount` is denominated in."""
  pocketName: NotRequired[str | None]
  """Name of the pocket on this side of the transaction, or null when this side is not a pocket."""
  pocketId: NotRequired[str | None]
  """Identifier of the pocket on this side of the transaction, or null when this side is not a pocket."""
  bankAccount: NotRequired[str]
  """Bank account on this side of the transaction, when this side is a bank transfer."""
  email: NotRequired[str]
  """Email of the counterparty, when this side is another Bit2Me user identified by email."""
  phone: NotRequired[TransactionDestinationPhone]
  alias: NotRequired[str]
  """Alias of the counterparty, when this side is another Bit2Me user identified by alias."""
  fullName: NotRequired[str]
  """Full name of the counterparty."""
  address: NotRequired[str | None]
  """Blockchain address on this side of the transaction, or null when this side is not a blockchain address."""
  addressNetwork: NotRequired[str | None]
  """Blockchain network of `address` (e.g. `ethereum`), or null when not applicable."""
  addressTag: NotRequired[str | None]
  """Memo/tag some blockchain networks require to route funds to `address`, or null when not applicable."""
  addressInBlacklist: NotRequired[bool | None]
  """Whether `address` is flagged on an anti-money-laundering blacklist, or null when not applicable."""
  amount: NotRequired[Decimal]
  """Amount of `currency` on this side of the transaction."""
  amountAfterFees: NotRequired[Decimal]
  """Amount of `currency` on this side of the transaction, after fees are deducted."""
  rate: NotRequired[TransactionDestinationRate]
  converted: NotRequired[TransactionDestinationConverted]
  userAmount: NotRequired[TransactionDestinationUserAmount]
  userId: NotRequired[str]
  """Identifier of the Bit2Me user on this side of the transaction, when this side is another Bit2Me user."""


class TransactionFee(TypedDict):
  """Fees charged for the transaction. `network` is present for withdrawals, `flip` when the transaction included a currency conversion, and `teller` for teller/card-related fees."""

  network: NotRequired[TransactionNetworkFee]
  flip: NotRequired[TransactionFlipFee]
  teller: NotRequired[TransactionTellerFee]


class TransactionFlip(TypedDict):
  """Currency conversion applied to the transaction, when applicable."""

  rate: NotRequired[TransactionFlipRate]


TransactionOriginKeywords = TypedDict(
  'TransactionOriginKeywords', {'class': NotRequired[str]}
)
"""
- `class`: Kind of counterparty this side of the transaction represents, e.g. `pocket`, `blockchain`, `trading`, `earn` (observed values; not declared as a closed set, see the endpoint `notes`).
"""


class TransactionOrigin(TransactionOriginKeywords):
  """The origin side of the transaction: a pocket, a blockchain address, a bank account, a card, or another Bit2Me user."""

  currency: NotRequired[str]
  """Currency `amount` is denominated in."""
  pocketName: NotRequired[str | None]
  """Name of the pocket on this side of the transaction, or null when this side is not a pocket."""
  pocketId: NotRequired[str | None]
  """Identifier of the pocket on this side of the transaction, or null when this side is not a pocket."""
  bankAccount: NotRequired[str]
  """Bank account on this side of the transaction, when this side is a bank transfer."""
  email: NotRequired[str]
  """Email of the counterparty, when this side is another Bit2Me user identified by email."""
  phone: NotRequired[TransactionOriginPhone]
  alias: NotRequired[str]
  """Alias of the counterparty, when this side is another Bit2Me user identified by alias."""
  fullName: NotRequired[str]
  """Full name of the counterparty."""
  address: NotRequired[str | None]
  """Blockchain address on this side of the transaction, or null when this side is not a blockchain address."""
  addressNetwork: NotRequired[str | None]
  """Blockchain network of `address` (e.g. `ethereum`), or null when not applicable."""
  addressTag: NotRequired[str | None]
  """Memo/tag some blockchain networks require to route funds to `address`, or null when not applicable."""
  addressInBlacklist: NotRequired[bool | None]
  """Whether `address` is flagged on an anti-money-laundering blacklist, or null when not applicable."""
  amount: NotRequired[Decimal]
  """Amount of `currency` on this side of the transaction."""
  amountAfterFees: NotRequired[Decimal]
  """Amount of `currency` on this side of the transaction, after fees are deducted."""
  rate: NotRequired[TransactionOriginRate]
  converted: NotRequired[TransactionOriginConverted]
  userAmount: NotRequired[TransactionOriginUserAmount]
  userId: NotRequired[str]
  """Identifier of the Bit2Me user on this side of the transaction, when this side is another Bit2Me user."""


class TransactionUserRate(TypedDict):
  """Exchange rate to the user's preferred display currency."""

  rate: NotRequired[TransactionUserExchangeRate]


class TransactionCompany(TypedDict):
  """Details of a company-side counterpart to the transaction, when applicable."""

  destination: NotRequired[TransactionCompanyDestination]


class WalletTransaction(TypedDict):
  """A single wallet transaction: a deposit, withdrawal, transfer, or internal movement of funds."""

  id: NotRequired[str]
  """Unique identifier of the transaction."""
  note: NotRequired[str | None]
  """Personal note the user attached to the transaction, or null when none was set."""
  date: NotRequired[datetime]
  """When the transaction was created (ISO 8601)."""
  completedAt: NotRequired[datetime | None]
  """When the transaction was completed (ISO 8601), or null while it has not completed."""
  canceledAt: NotRequired[datetime | None]
  """When the transaction was canceled (ISO 8601), or null when it was not canceled."""
  updatedAt: NotRequired[datetime | None]
  """When the transaction was last updated (ISO 8601). Not present on every transaction record."""
  concept: NotRequired[str]
  """Free-text concept of the transaction, as entered by the counterparty or the system."""
  type: NotRequired[str]
  """Broad category of the transaction, e.g. `deposit`, `withdrawal`, `transfer` (not declared as a closed set, see the endpoint `notes`)."""
  subtype: NotRequired[str]
  """Finer-grained classification of the transaction within its `type`, e.g. `trading`, `earn`, `receive`, `automatic-send`, `swap` (not declared as a closed set, see the endpoint `notes`)."""
  method: NotRequired[str]
  """Delivery mechanism of the transaction, e.g. `pocket` for an internal transfer or `blockchain` for an on-chain movement."""
  status: NotRequired[str]
  """Lifecycle status of the transaction, e.g. `completed` (not declared as a closed set, see the endpoint `notes`)."""
  substractFeeType: NotRequired[TransactionSubsFeeTypeParam | None]
  """Whether the transaction amount is what the receiver gets (`SEA`) or what is deducted from the sender's balance (`REA`); null when not applicable."""
  denomination: NotRequired[TransactionDenomination]
  frequency: NotRequired[str]
  """Recurrence frequency of the transaction, e.g. `punctual` for a one-off transaction; part of the recurring-order feature alongside `isInitialRecurringOrder`."""
  isInitialRecurringOrder: NotRequired[bool]
  """Whether this transaction is the first execution of a recurring order."""
  origin: NotRequired[TransactionOrigin]
  destination: NotRequired[TransactionDestination]
  transaction: NotRequired[TransactionNetworkDetails]
  fee: NotRequired[TransactionFee]
  flip: NotRequired[TransactionFlip]
  benefit: NotRequired[TransactionBenefit]
  userRate: NotRequired[TransactionUserRate]
  userAmount: NotRequired[TransactionUserAmount]
  instantId: NotRequired[str]
  """Identifier of the instant swap/conversion this transaction belongs to; present for `swap` transactions."""
  company: NotRequired[TransactionCompany]


class ListWalletTransactionsV3response(TypedDict):
  """One cursor-paginated page of wallet transactions."""

  data: list[WalletTransaction]
  """Transactions on this page, same shape as `v2.wallet.transactions`'s rows."""
  pageInfo: CursorPageInfo


validate_response = validator(ListWalletTransactionsV3response)


class Transactions(RpcEndpoint):
  async def transactions(
    self,
    *,
    cursor: str | None = None,
    limit: int | None = None,
    year: int | None = None,
    currency: str | None = None,
    operation: Literal[
      'purchase',
      'sell',
      'swap',
      'deposit',
      'withdrawal',
      'deposit-earn',
      'withdrawal-earn',
      'deposit-trading',
      'withdrawal-trading',
      'send-pay',
      'receive-pay',
      'purchase-bcard',
      'reimburse-bcard',
      'send',
      'receive',
    ]
    | None = None,
    teller_id: str | None = None,
    validate: bool | None = None,
  ) -> ListWalletTransactionsV3response:
    """Get user transactions with cursor-based pagination. Use the `endCursor` value from the previous response as the `cursor` parameter to fetch the next page.

    Args:
      cursor: Opaque cursor for pagination. Pass the previous response's `pageInfo.endCursor` to fetch the next page; omit to fetch the first page.
      limit: Maximum number of entries to return.
      year: Filter movements to this specific year.
      currency: Currency the movements are denominated in.
      operation: Operation to filter by.
      teller_id: Filter by the associated teller order id.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/Wallet/operation/getTransactionsV3)
    """
    params = {}
    if cursor is not None:
      params['cursor'] = cursor
    if limit is not None:
      params['limit'] = limit
    if year is not None:
      params['year'] = year
    if currency is not None:
      params['currency'] = currency
    if operation is not None:
      params['operation'] = operation
    if teller_id is not None:
      params['tellerId'] = teller_id
    return await self.request(
      'GET',
      '/v3/wallet/transaction',
      params=params,
      validator=validate_response,
      validate=validate,
    )

  async def transactions_paged(
    self,
    *,
    limit: int | None = None,
    year: int | None = None,
    currency: str | None = None,
    operation: Literal[
      'purchase',
      'sell',
      'swap',
      'deposit',
      'withdrawal',
      'deposit-earn',
      'withdrawal-earn',
      'deposit-trading',
      'withdrawal-trading',
      'send-pay',
      'receive-pay',
      'purchase-bcard',
      'reimburse-bcard',
      'send',
      'receive',
    ]
    | None = None,
    teller_id: str | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[ListWalletTransactionsV3response]:
    """Yield successive pages of `transactions`.

    Passes each page's token back as `cursor` and stops when a response carries no
    `pageInfo.endCursor`, or after `max_pages` pages when one is given.
    """
    cursor: str | None = None
    pages = 0
    while True:
      response = await self.transactions(
        limit=limit,
        year=year,
        currency=currency,
        operation=operation,
        teller_id=teller_id,
        cursor=cursor,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      cursor_0 = response.get('pageInfo') if response is not None else None
      cursor = cursor_0.get('endCursor') if cursor_0 is not None else None
      if not cursor:
        break
