"""Wire shapes of Kraken Futures' private REST endpoints.

Numbers come as JSON numbers or strings depending on the endpoint; every quantity,
price and amount is validated into a `Decimal`.
"""

from datetime import datetime
from decimal import Decimal
from typing_extensions import Literal, NotRequired

from typed_core.validation import TypedDict

OrderType = Literal['lmt', 'post', 'ioc', 'mkt', 'stp', 'take_profit', 'trailing_stop']
"""Order types `sendorder` accepts: `lmt` rests, `post` is post-only, `ioc` is
immediate-or-cancel and `mkt` an IOC bounded only by the venue's price collar."""

Side = Literal['buy', 'sell']

QtyMode = Literal['ABSOLUTE', 'RELATIVE']
"""How an edit's `size` is read: `ABSOLUTE` sets the total order size, past fills
included; `RELATIVE` (Kraken's default) sets the remaining open size."""


class FlexCurrency(TypedDict):
  """One currency held in the multi-collateral (flex) account."""

  quantity: Decimal
  """Amount held, in the currency's own units."""
  value: NotRequired[Decimal]
  """USD value of `quantity`."""
  collateral: NotRequired[Decimal]
  """USD value counted as margin, after the currency's haircut."""
  available: NotRequired[Decimal]
  """Amount free to withdraw or transfer."""


class FlexAccount(TypedDict):
  """The multi-collateral margin account, which backs every `PF_` contract.

  All values are USD.
  """

  type: Literal['multiCollateralMarginAccount']
  currencies: dict[str, FlexCurrency]
  initialMargin: Decimal
  """Initial margin of open positions."""
  initialMarginWithOrders: Decimal
  """Initial margin of open positions and open orders."""
  maintenanceMargin: Decimal
  """Maintenance margin of open positions; liquidation when `marginEquity` falls to it."""
  balanceValue: Decimal
  """USD value of all currencies held, before haircuts."""
  portfolioValue: Decimal
  """`balanceValue` plus unrealized P&L."""
  collateralValue: Decimal
  """USD value of all currencies held, after haircuts."""
  pnl: Decimal
  """Unrealized P&L of open positions."""
  unrealizedFunding: Decimal
  """Funding accrued but not yet realized."""
  totalUnrealized: Decimal
  """Unrealized P&L and funding."""
  totalUnrealizedAsMargin: Decimal
  """`totalUnrealized` as counted towards margin."""
  availableMargin: Decimal
  """Margin free for new orders: `marginEquity` less `initialMarginWithOrders`."""
  marginEquity: Decimal
  """Collateral value plus unrealized P&L counted as margin: the account's equity."""


class CashAccount(TypedDict):
  """The cash (holding) account, outside margin."""

  type: Literal['cashAccount']
  balances: dict[str, Decimal]


class MarginAccount(TypedDict):
  """A legacy single-collateral margin account (inverse and `FI_` contracts)."""

  type: Literal['marginAccount']
  currency: str
  balances: dict[str, Decimal]


class OtherAccount(TypedDict):
  """An account type this client does not model."""

  type: str


class AccountsResult(TypedDict):
  """`GET /accounts`: every account of the key's user, keyed by account name (the
  multi-collateral one is `flex`)."""

  result: Literal['success']
  accounts: dict[str, FlexAccount | CashAccount | MarginAccount | OtherAccount]
  serverTime: datetime


class OpenPosition(TypedDict):
  """One open position."""

  side: Literal['long', 'short']
  symbol: str
  price: Decimal
  """Average entry price."""
  fillTime: datetime
  size: Decimal
  """Unsigned size in contracts; `side` gives the direction."""
  unrealizedFunding: NotRequired[Decimal | None]
  pnlCurrency: NotRequired[str | None]
  maxFixedLeverage: NotRequired[Decimal | None]
  """The isolated position's leverage; absent for a cross position."""


class OpenPositionsResult(TypedDict):
  """`GET /openpositions`."""

  result: Literal['success']
  openPositions: list[OpenPosition]
  serverTime: datetime


class OpenOrder(TypedDict):
  """One open order, as `GET /openorders` lists it."""

  order_id: str
  cliOrdId: NotRequired[str | None]
  status: str
  """`untouched` or `partiallyFilled`."""
  side: Side
  orderType: str
  """`lmt` (post-only orders included), `stop`, `take_profit`, ..."""
  symbol: str
  limitPrice: NotRequired[Decimal | None]
  stopPrice: NotRequired[Decimal | None]
  filledSize: Decimal
  unfilledSize: Decimal
  reduceOnly: bool
  receivedTime: datetime
  lastUpdateTime: datetime


class OpenOrdersResult(TypedDict):
  """`GET /openorders`."""

  result: Literal['success']
  openOrders: list[OpenOrder]
  serverTime: datetime


class EventOrder(TypedDict):
  """An order as order events carry it."""

  orderId: str
  cliOrdId: NotRequired[str | None]
  type: str
  """`lmt`, `post`, `ioc`, `mkt`, ..."""
  symbol: str
  side: Side
  quantity: Decimal
  filled: Decimal
  limitPrice: NotRequired[Decimal | None]
  reduceOnly: bool
  timestamp: datetime
  lastUpdateTimestamp: NotRequired[datetime]


class PlaceEvent(TypedDict):
  """The order now rests."""

  type: Literal['PLACE']
  order: EventOrder
  reducedQuantity: NotRequired[Decimal | None]


class ExecutionEvent(TypedDict):
  """The order filled `amount` contracts at `price`."""

  type: Literal['EXECUTION']
  executionId: str
  price: Decimal
  amount: Decimal
  orderPriorExecution: EventOrder
  orderPriorEdit: NotRequired[EventOrder | None]
  takerReducedQuantity: NotRequired[Decimal | None]


class CancelEvent(TypedDict):
  """The order no longer rests, e.g. an IOC remainder or a cancel."""

  type: Literal['CANCEL']
  order: EventOrder
  uid: NotRequired[str]


class EditEvent(TypedDict):
  """The order was edited in place."""

  type: Literal['EDIT']
  old: EventOrder
  new: EventOrder
  reducedQuantity: NotRequired[Decimal | None]


class RejectEvent(TypedDict):
  """The order was refused."""

  type: Literal['REJECT']
  order: NotRequired[EventOrder]
  reason: NotRequired[str]
  uid: NotRequired[str]


class OtherEvent(TypedDict):
  """An event type this client does not model (e.g. trigger events)."""

  type: str


OrderEvent = (
  PlaceEvent | ExecutionEvent | CancelEvent | EditEvent | RejectEvent | OtherEvent
)

SendStatusCode = Literal[
  'placed',
  'partiallyFilled',
  'filled',
  'cancelled',
  'edited',
  'marketSuspended',
  'marketInactive',
  'invalidPrice',
  'invalidSize',
  'tooManySmallOrders',
  'insufficientAvailableFunds',
  'wouldCauseLiquidation',
  'clientOrderIdAlreadyExist',
  'clientOrderIdTooBig',
  'maxPositionViolation',
  'outsidePriceCollar',
  'wouldIncreasePriceDislocation',
  'notFound',
  'orderForEditNotAStop',
  'orderForEditNotFound',
  'postWouldExecute',
  'iocWouldNotExecute',
  'selfFill',
  'wouldNotReducePosition',
  'marketIsPostOnly',
  'tooManyOrders',
  'fixedLeverageTooHigh',
  'clientOrderIdInvalid',
  'cannotEditTriggerPriceOfTrailingStop',
  'cannotEditLimitPriceOfTrailingStop',
  'wouldProcessAfterSpecifiedTime',
]
"""Placement statuses; only `placed` (and an edit's `edited`) mean the order was accepted."""


class SendStatus(TypedDict):
  """`sendorder`'s outcome."""

  status: str
  """A `SendStatusCode`; kept open since the venue adds codes."""
  order_id: NotRequired[str]
  cliOrdId: NotRequired[str | None]
  receivedTime: NotRequired[datetime]
  orderEvents: NotRequired[list[OrderEvent]]


class SendOrderResult(TypedDict):
  """`POST /sendorder`."""

  result: Literal['success']
  sendStatus: SendStatus
  serverTime: datetime


class EditStatus(TypedDict):
  """`editorder`'s outcome."""

  status: str
  """`edited`, or the reason it was not (`orderForEditNotFound`, `postWouldExecute`, ...)."""
  orderId: NotRequired[str]
  cliOrdId: NotRequired[str | None]
  receivedTime: NotRequired[datetime]
  orderEvents: NotRequired[list[OrderEvent]]


class EditOrderResult(TypedDict):
  """`POST /editorder`."""

  result: Literal['success']
  editStatus: EditStatus
  serverTime: datetime


class CancelStatus(TypedDict):
  """`cancelorder`'s outcome."""

  status: str
  """`cancelled`, `filled` or `notFound`."""
  order_id: NotRequired[str]
  cliOrdId: NotRequired[str | None]
  receivedTime: NotRequired[datetime]
  orderEvents: NotRequired[list[OrderEvent]]


class CancelOrderResult(TypedDict):
  """`POST /cancelorder`."""

  result: Literal['success']
  cancelStatus: CancelStatus
  serverTime: datetime


class BatchStatus(TypedDict):
  """One instruction's outcome in a batch."""

  status: str
  order_tag: NotRequired[str]
  order_id: NotRequired[str]
  cliOrdId: NotRequired[str | None]
  dateTimeReceived: NotRequired[datetime | None]
  orderEvents: NotRequired[list[OrderEvent]]


class BatchOrderResult(TypedDict):
  """`POST /batchorder`."""

  result: Literal['success']
  batchStatus: list[BatchStatus]
  serverTime: datetime


class BatchSend(TypedDict):
  """A batch instruction placing an order."""

  order: Literal['send']
  order_tag: str
  """Echoed on its `BatchStatus`."""
  orderType: OrderType
  symbol: str
  side: Side
  size: Decimal
  limitPrice: NotRequired[Decimal]
  cliOrdId: NotRequired[str]
  reduceOnly: NotRequired[bool]


class BatchEdit(TypedDict):
  """A batch instruction editing an order."""

  order: Literal['edit']
  order_id: NotRequired[str]
  cliOrdId: NotRequired[str]
  size: NotRequired[Decimal]
  """New size, read per `qtyMode`: the remaining open size unless `ABSOLUTE`."""
  limitPrice: NotRequired[Decimal]
  qtyMode: NotRequired[QtyMode]
  """How `size` is read; Kraken defaults to `RELATIVE`."""


class BatchCancel(TypedDict):
  """A batch instruction cancelling an order."""

  order: Literal['cancel']
  order_id: NotRequired[str]
  cliOrdId: NotRequired[str]


BatchInstruction = BatchSend | BatchEdit | BatchCancel


class CancelAllStatus(TypedDict):
  """`cancelallorders`' outcome."""

  status: str
  receivedTime: NotRequired[datetime]
  cancelOrderEvents: NotRequired[list[dict]]
  cancelledOrders: NotRequired[list[dict]]


class CancelAllResult(TypedDict):
  """`POST /cancelallorders`."""

  result: Literal['success']
  cancelStatus: CancelAllStatus
  serverTime: datetime


class OrderStatusOrder(TypedDict):
  """An order as `orders/status` reports it."""

  type: str
  orderId: str
  cliOrdId: NotRequired[str | None]
  symbol: str
  side: Side
  quantity: Decimal
  filled: Decimal
  limitPrice: NotRequired[Decimal | None]
  reduceOnly: bool
  timestamp: datetime
  lastUpdateTimestamp: NotRequired[datetime]


class OrderStatusEntry(TypedDict):
  """One order's status."""

  order: OrderStatusOrder
  status: str
  """`ENTERED_BOOK`, `FULLY_EXECUTED`, `REJECTED`, `CANCELLED`, `TRIGGER_PLACED`,
  `TRIGGER_ACTIVATION_FAILURE`."""
  updateReason: NotRequired[str | None]
  error: NotRequired[str | None]


class OrderStatusResult(TypedDict):
  """`GET /orders/status`."""

  result: Literal['success']
  orders: list[OrderStatusEntry]
  serverTime: datetime


class Fill(TypedDict):
  """One own fill, as `GET /fills` lists it (without its fee)."""

  fill_id: str
  symbol: str
  side: Side
  order_id: str
  cliOrdId: NotRequired[str | None]
  size: Decimal
  price: Decimal
  fillTime: datetime
  fillType: str
  """`maker`, `taker`, `liquidation`, `assignor`, `assignee`, `takerAfterEdit`,
  `unwindBankrupt`, `unwindCounterparty`."""


class FillsResult(TypedDict):
  """`GET /fills`: the last 100 fills up to `lastFillTime`, newest first."""

  result: Literal['success']
  fills: list[Fill]
  serverTime: datetime


class LeveragePreference(TypedDict):
  """A market set to isolated margin, at `maxLeverage`."""

  symbol: str
  maxLeverage: Decimal


class LeveragePreferencesResult(TypedDict):
  """`GET /leveragepreferences`: markets without a row trade on cross margin."""

  result: Literal['success']
  leveragePreferences: list[LeveragePreference]
  serverTime: datetime


class FeeTier(TypedDict):
  """One volume tier of a fee schedule; fees are in percent."""

  makerFee: Decimal
  takerFee: Decimal
  usdVolume: Decimal


class FeeSchedule(TypedDict):
  """A fee schedule instruments refer to by `feeScheduleUid`."""

  uid: str
  name: str
  tiers: list[FeeTier]


class FeeSchedulesResult(TypedDict):
  """`GET /feeschedules`."""

  result: Literal['success']
  feeSchedules: list[FeeSchedule]
  serverTime: datetime


class FeeVolumesResult(TypedDict):
  """`GET /feeschedules/volumes`: the account's 30-day USD volume per fee schedule."""

  result: Literal['success']
  volumesByFeeSchedule: dict[str, Decimal]
  serverTime: datetime


class AccountLogEntry(TypedDict, total=False):
  """One account log row; funding rows have `info` `funding rate change`."""

  id: int
  date: datetime
  asset: str
  info: str
  contract: str | None
  realized_funding: Decimal | None
  new_balance: Decimal | None
  old_balance: Decimal | None


class AccountLogResult(TypedDict):
  """`GET /api/history/v3/account-log`, newest first."""

  accountUid: NotRequired[str]
  logs: list[AccountLogEntry]
