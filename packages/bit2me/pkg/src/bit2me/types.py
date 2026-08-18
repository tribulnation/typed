from decimal import Decimal
from datetime import datetime
from typing_extensions import Any, Literal, NotRequired, TypedDict


class BooleanResultResponse(TypedDict):
  result: bool


class CreatedResourceIdResponse(TypedDict):
  id: str
  """Identifier of the created resource (e.g. executed wallet transaction)"""


class CustomerRequestTransaction(TypedDict):
  userId: str
  amount: Decimal
  pair: Literal['BTC/EUR', 'B2M/EUR', '...']
  createdAt: datetime


class DepositEstimation(TypedDict):
  minimum: int
  maximum: int


class EarnRewardsConfigResponse(TypedDict):
  walletId: NotRequired[str]
  userId: NotRequired[str]
  currency: NotRequired[str]
  rewardCurrency: NotRequired[str]
  createdAt: NotRequired[datetime]
  updatedAt: NotRequired[datetime]


class EarnWalletRecordConvertedBalance(TypedDict):
  value: NotRequired[str]
  currency: NotRequired[str]


class FundsOrigin(TypedDict):
  type: Literal[
    'salary',
    'incomes',
    'investments',
    'pensions',
    'donations',
    'propertiesSell',
    'others',
  ]
  othersReason: NotRequired[str]


class ItemConvertedBalance(TypedDict):
  value: NotRequired[str]
  currency: NotRequired[str]


class LoanAction(TypedDict):
  orderId: NotRequired[str]
  createdAt: NotRequired[datetime]
  updatedAt: NotRequired[datetime]
  userId: NotRequired[str]
  requestedByUserId: NotRequired[str]
  guaranteeCurrency: NotRequired[str]
  guaranteeOriginalAmount: NotRequired[str]
  guaranteeAmount: NotRequired[str]
  loanCurrency: NotRequired[str]
  loanOriginalAmount: NotRequired[str]
  loanAmount: NotRequired[str]
  paybackAmount: NotRequired[str]
  ltv: NotRequired[str]
  apr: NotRequired[str]
  status: NotRequired[str]
  startedAt: NotRequired[datetime]
  finishedAt: NotRequired[datetime]
  expiresAt: NotRequired[datetime]
  paybackPrincipalAmount: NotRequired[str]
  paybackInterestAmount: NotRequired[str]
  interestAmount: NotRequired[str]


class LockPeriod(TypedDict):
  lockPeriodId: NotRequired[str]
  months: NotRequired[int]


MillisTimestamp = int

OffsetParam = int


class OrderResponse(TypedDict):
  id: NotRequired[str]
  """Order identifier"""
  userId: NotRequired[str]
  """User identifier"""
  side: NotRequired[Literal['buy', 'sell']]
  """Order direction"""
  symbol: NotRequired[str]
  """Market symbol"""
  fromCurrency: NotRequired[str]
  """Base currency"""
  toCurrency: NotRequired[str]
  """Quote currency"""
  price: NotRequired[Decimal]
  stopPrice: NotRequired[Decimal]
  amount: NotRequired[Decimal]
  orderAmount: NotRequired[Decimal]
  filledAmount: NotRequired[Decimal]
  """Filled order size in terms of base currency"""
  dustAmount: NotRequired[Decimal]
  """Difference amount between the order amount and the filled amount when the order status is filled"""
  feeAmount: NotRequired[Decimal]
  """Fee percentage respect to trade amount `amount`"""
  feeCurrency: NotRequired[str | None]
  """Field `feeAmount` currency"""
  status: NotRequired[Literal['open', 'filled', 'cancelled', 'inactive']]
  """Order status. The stop limit order remains inactive until the stop price is reached, then it becomes open or filled"""
  orderType: NotRequired[Literal['limit', 'stop-limit', 'market']]
  """Order type"""
  cost: NotRequired[Decimal]
  """Total cost by multiplying amount by price"""
  createdAt: NotRequired[datetime]
  """Date time in ISO 8601 string format"""
  updatedAt: NotRequired[datetime]
  """Date time in ISO 8601 string format"""
  cancelReason: NotRequired[str | None]
  """Detailed message about order cancel reason"""
  clientOrderId: NotRequired[str | None]
  """Client order internal identifier"""
  postOnly: NotRequired[bool | None]
  timeInForce: NotRequired[Literal['GTC', 'IOC', 'FOK']]
  """Time-in-force of the order to specify how long it should remain in the order book before being cancelled:
GTC (Good-'til-cancelled) is default if the parameter is omitted.
IOC (Immediate-or-cancel) will immediately execute the amount possible and cancel any remaining balance rather than resting in the book.
FOK (Fill-or-kill) will immediately wait for order to be fully executed without taking the risk of receiving partial fills"""


OrderSide = Literal['buy', 'sell']

OrderStatus = Literal['open', 'filled', 'cancelled', 'inactive']

OrderType = Literal['limit', 'stop-limit', 'market']


class Pair(TypedDict):
  base: str
  """Valid currency symbol"""
  quote: str
  """Valid currency symbol"""


PayOrderStatus = Literal[
  'waiting-funds', 'pending', 'accepted', 'cancelled', 'expired', 'error'
]

PayOrderType = Literal['email', 'phone', 'alias']


class Phone(TypedDict):
  number: str
  countryCode: str


PocketColor = int

PointsParam = int

PostOnlyParam = bool

SortDirectionParam = Literal['asc', 'desc']


class StatusChangesItem(TypedDict):
  newStatus: NotRequired[
    Literal['waiting-funds', 'pending', 'accepted', 'cancelled', 'expired', 'error']
  ]
  author: NotRequired[str]
  created: NotRequired[datetime]
  reason: NotRequired[str]


TimeInForce = Literal['GTC', 'IOC', 'FOK']


class TokenResponse(TypedDict):
  token: str
  expirationTime: int


class TradeResponse(TypedDict):
  id: NotRequired[str]
  """Trade identifier"""
  orderId: NotRequired[str]
  """Order identifier"""
  symbol: NotRequired[str]
  """Market symbol"""
  side: NotRequired[Literal['buy', 'sell']]
  """Order direction"""
  orderType: NotRequired[Literal['limit', 'stop-limit', 'market']]
  """Order type"""
  price: NotRequired[Decimal]
  """Spot API may return numeric or string decimals"""
  amount: NotRequired[Decimal]
  """Spot API may return numeric or string decimals"""
  priceCurrency: NotRequired[str]
  """Field `price` currency"""
  amountCurrency: NotRequired[str]
  """Field `amount` currency"""
  isMaker: NotRequired[bool]
  """`true` if trade was executed with user as the maker, `false` if taker"""
  createdAt: NotRequired[datetime]
  """Date time in ISO 8601 string format"""
  cost: NotRequired[Decimal]
  """Total cost (quote currency)"""
  costEuro: NotRequired[Decimal]
  """Total cost (EURO currency)"""
  clientOrderId: NotRequired[str | None]
  """Client order internal identifier (null when not set)"""
  feeAmount: NotRequired[Decimal]
  """Fee amount (currency indicated by `feeCurrency` field)"""
  feePercentage: NotRequired[Decimal]
  """Fee percentage respect to trade amount `amount`"""
  feeCurrency: NotRequired[str]
  """Field `feeAmount` currency"""


TransactionSubsFeeTypeParam = Literal['SEA', 'REA']


class UserAddress(TypedDict):
  id: NotRequired[str]
  userId: NotRequired[str]
  alias: NotRequired[str]
  streetAddress: str
  city: str
  stateCode: str
  """Value obtained from 'fips' (Federal Information Processing Standard  (https://en.wikipedia.org/wiki/Federal_Information_Processing_Standards)) field in /v1/misc/country/{countryISOCode}/region response.

  Additional information of this endpoint is available in misc section"""
  zip: str
  countryCode: str
  isResidence: NotRequired[bool]
  isDefaultAddress: NotRequired[bool]


UserType = Literal['person', 'company', 'employee']


class WalletResponse(TypedDict):
  id: NotRequired[str]
  """Wallet identifier"""
  userId: NotRequired[str]
  """User identifier"""
  currency: NotRequired[str]
  """Valid currency symbol"""
  balance: NotRequired[Decimal]
  """Balance available"""
  blockedBalance: NotRequired[Decimal]
  """Balance in use on active orders"""
  createdAt: NotRequired[datetime]
  """Date time in ISO 8601 string format"""


class DataItem(TypedDict):
  walletId: NotRequired[str]
  userId: NotRequired[str]
  currency: NotRequired[str]
  balance: NotRequired[str]
  lockPeriod: NotRequired[LockPeriod]
  convertedBalance: NotRequired[ItemConvertedBalance]
  createdAt: NotRequired[datetime]
  updatedAt: NotRequired[datetime]


class EarnWalletRecord(TypedDict):
  """Single Earn wallet returned by GET /v1/earn/wallets/{walletId}"""

  walletId: NotRequired[str]
  userId: NotRequired[str]
  currency: NotRequired[str]
  balance: NotRequired[str]
  createdAt: NotRequired[datetime]
  updatedAt: NotRequired[datetime]
  convertedBalance: NotRequired[EarnWalletRecordConvertedBalance]
  lockPeriod: NotRequired[dict[str, Any]]


class PayOrderData(TypedDict):
  orderId: str
  createdAt: datetime
  expiryDate: datetime
  userId: str
  pocketId: str
  type: Literal['email', 'phone', 'alias']
  email: NotRequired[str]
  phone: NotRequired[Phone]
  currency: str
  amount: Decimal
  status: Literal[
    'waiting-funds', 'pending', 'accepted', 'cancelled', 'expired', 'error'
  ]
  statusChanges: list[StatusChangesItem]
  senderName: str
  alias: NotRequired[str]
  note: NotRequired[str]
  walletMovementId: str


class RateRate(TypedDict):
  value: Decimal
  pair: Pair


class EarnWalletResponse(TypedDict):
  total: NotRequired[int]
  data: NotRequired[list[DataItem]]


class Rate(TypedDict):
  rate: NotRequired[RateRate]


class AmountCurrencyObject(TypedDict):
  amount: Decimal
  currency: str
  """Valid currency symbol"""
  rate: NotRequired[Rate]
