"""`POST /api/v1/copy-trade/futures/position/margin/deposit-margin` — Add Isolated Margin."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class AddCopyTradeIsolatedMarginParams(TypedDict):
  """Symbol, position side, amount and idempotency key for an isolated-margin deposit."""

  symbol: str
  """Contract symbol, e.g. `XBTUSDTM`."""
  margin: float
  """Margin amount to add."""
  positionSide: Literal['LONG', 'SHORT']
  """Position side."""
  bizNo: str
  """Caller-generated unique id ensuring the deposit is processed only once."""


class CopyTradeIsolatedMarginDepositResult(TypedDict):
  """A copy-trading futures position's detail as returned right after an isolated-margin deposit. Broader than `futures.positions.add_isolated_margin`'s equivalent `IsolatedMarginDepositResult` -- this variant additionally carries `marginMode`/`positionSide`/`leverage` (Hedge Mode fields Copy Trading exposes directly) and has no `userId`. Never called; field list and types are as rendered by the venue's docs page, unconfirmed live."""

  id: str
  """Position ID."""
  symbol: str
  """Symbol of the contract."""
  autoDeposit: bool
  """Whether margin is automatically deposited to avoid liquidation."""
  maintMarginReq: str
  """Maintenance margin requirement."""
  riskLimit: int
  """Risk limit level."""
  realLeverage: str
  """Leverage actually in effect for the position."""
  crossMode: bool
  """Whether this is a cross-margin position."""
  marginMode: Literal['ISOLATED', 'CROSS']
  """Margin mode. Presumably always `ISOLATED` for a result of adding isolated margin, but not confirmed live."""
  positionSide: Literal['LONG', 'SHORT']
  """Position side."""
  leverage: str
  """Leverage the position is using."""
  delevPercentage: float
  """ADL ranking percentile."""
  openingTimestamp: int
  """First opening time, Unix milliseconds."""
  currentTimestamp: int
  """Current server timestamp, Unix milliseconds."""
  currentQty: int
  """Current position quantity."""
  currentCost: str
  """Current position value."""
  currentComm: str
  """Current commission."""
  unrealisedCost: str
  """Unrealised value."""
  realisedGrossCost: str
  """Accumulated realised gross profit value."""
  realisedCost: str
  """Current realised position value."""
  isOpen: bool
  """Whether the position is currently open."""
  markPrice: str
  """Mark price."""
  markValue: str
  """Value at mark price."""
  posCost: str
  """Position value."""
  posCross: str
  """Added margin."""
  posInit: str
  """Leverage margin."""
  posComm: str
  """Bankruptcy cost."""
  posLoss: str
  """Funding fees paid out."""
  posMargin: str
  """Position margin."""
  posMaint: str
  """Maintenance margin."""
  maintMargin: str
  """Position margin."""
  realisedGrossPnl: str
  """Accumulated realised gross profit value."""
  realisedPnl: str
  """Realised profit and loss."""
  unrealisedPnl: str
  """Unrealised profit and loss."""
  unrealisedPnlPcnt: str
  """Profit-loss ratio of the position."""
  unrealisedRoePcnt: str
  """Rate of return on investment."""
  avgEntryPrice: str
  """Average entry price."""
  liquidationPrice: str
  """Liquidation price."""
  bankruptPrice: str
  """Bankruptcy price."""
  settleCurrency: str
  """Currency used to clear and settle the trades."""


_Type = CopyTradeIsolatedMarginDepositResult
adapter = validator[_Type](_Type)  # type: ignore


class AddIsolatedMargin(RpcEndpoint):
  """`Add Isolated Margin` — mixed into `CopyTrading`, the product exposing `copy_trading.add_isolated_margin`."""

  async def add_isolated_margin(
    self,
    add_copy_trade_isolated_margin_params: AddCopyTradeIsolatedMarginParams,
    *,
    validate: bool | None = None,
  ) -> CopyTradeIsolatedMarginDepositResult:
    """Manually add isolated margin to an existing copy-trading isolated position. Requires the API key's `LeadtradeFutures` permission.

    Args:
      add_copy_trade_isolated_margin_params: Symbol, side, amount and idempotency key for the isolated-margin deposit.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/copy-trade/futures/position/margin/deposit-margin',
      json=add_copy_trade_isolated_margin_params,
      validator=adapter,
      validate=validate,
    )
