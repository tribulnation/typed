"""Kraken Futures private REST: account, positions, orders, fills, leverage and fees."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing_extensions import Sequence

from typed_core.validation import validator

from .http import SignedFuturesHttpClient
from .types import (
  AccountLogResult,
  AccountsResult,
  BatchInstruction,
  BatchOrderResult,
  CancelAllResult,
  CancelOrderResult,
  EditOrderResult,
  FeeSchedulesResult,
  FeeVolumesResult,
  FillsResult,
  LeveragePreferencesResult,
  OpenOrdersResult,
  OpenPositionsResult,
  OrderStatusResult,
  OrderType,
  SendOrderResult,
  Side,
)

API = '/derivatives/api/v3'
HISTORY = '/api/history/v3'


def iso(time: datetime) -> str:
  """An aware datetime in the ISO-8601 UTC form Kraken's REST parameters take."""
  if time.utcoffset() is None:
    raise ValueError('Kraken Futures times must be timezone-aware')
  return time.isoformat().replace('+00:00', 'Z')


@dataclass(frozen=True, kw_only=True)
class FuturesTrading:
  """Kraken Futures' authenticated REST endpoints.

  Rate limits: every `/derivatives` call spends from a budget of 500 points per 10
  seconds (`sendorder`, `editorder` and `cancelorder` 10 each, `batchorder` 9 plus its
  size, `accounts`, `openpositions` and `openorders` 2, `fills` 2 or 25 with
  `lastFillTime`, `cancelallorders` 25); history calls have a separate budget. An
  exhausted budget answers `apiLimitExceeded`, raised as `RateLimited`.

  References:
    - [Futures REST API](https://docs.kraken.com/api/docs/futures-api/trading/account-information)
    - [Rate limits](https://docs.kraken.com/api/docs/guides/futures-rate-limits)
  """

  client: SignedFuturesHttpClient

  async def accounts(self, *, validate: bool | None = None) -> AccountsResult:
    """Every account of the user: `flex` is the multi-collateral one."""
    return await self.client.signed(
      'GET', f'{API}/accounts', validator=validator(AccountsResult), validate=validate
    )

  async def open_positions(
    self, *, validate: bool | None = None
  ) -> OpenPositionsResult:
    """Every open position."""
    return await self.client.signed(
      'GET',
      f'{API}/openpositions',
      validator=validator(OpenPositionsResult),
      validate=validate,
    )

  async def open_orders(self, *, validate: bool | None = None) -> OpenOrdersResult:
    """Every open order, of every market."""
    return await self.client.signed(
      'GET',
      f'{API}/openorders',
      validator=validator(OpenOrdersResult),
      validate=validate,
    )

  async def order_status(
    self,
    order_ids: Sequence[str] = (),
    *,
    cli_ord_ids: Sequence[str] = (),
    validate: bool | None = None,
  ) -> OrderStatusResult:
    """The status of orders by ID or client order ID, open or recently closed."""
    params: list[tuple[str, str]] = [('orderIds', id) for id in order_ids]
    params += [('cliOrdIds', id) for id in cli_ord_ids]
    return await self.client.signed(
      'GET',
      f'{API}/orders/status',
      params,
      validator=validator(OrderStatusResult),
      validate=validate,
    )

  async def send_order(
    self,
    *,
    order_type: OrderType,
    symbol: str,
    side: Side,
    size: Decimal,
    limit_price: Decimal | None = None,
    cli_ord_id: str | None = None,
    reduce_only: bool | None = None,
    validate: bool | None = None,
  ) -> SendOrderResult:
    """Place an order.

    Args:
      order_type: `lmt`, `post` (post-only), `ioc`, or `mkt`.
      symbol: Instrument, e.g. `PF_XBTUSD`.
      side: `buy` or `sell`.
      size: Contracts, unsigned.
      limit_price: Required for `lmt`, `post` and `ioc`.
      cli_ord_id: Your own ID, up to 100 characters, unique among open orders.
      reduce_only: Only reduce the position.
    """
    return await self.client.signed(
      'POST',
      f'{API}/sendorder',
      {
        'orderType': order_type,
        'symbol': symbol,
        'side': side,
        'size': size,
        'limitPrice': limit_price,
        'cliOrdId': cli_ord_id,
        'reduceOnly': reduce_only,
      },
      validator=validator(SendOrderResult),
      validate=validate,
    )

  async def edit_order(
    self,
    *,
    order_id: str | None = None,
    cli_ord_id: str | None = None,
    size: Decimal | None = None,
    limit_price: Decimal | None = None,
    validate: bool | None = None,
  ) -> EditOrderResult:
    """Edit a resting order's size or price in place.

    Args:
      order_id: The order to edit; or `cli_ord_id`.
      cli_ord_id: The order's client ID.
      size: New total size, filled part included.
      limit_price: New limit price.
    """
    return await self.client.signed(
      'POST',
      f'{API}/editorder',
      {
        'orderId': order_id,
        'cliOrdId': cli_ord_id,
        'size': size,
        'limitPrice': limit_price,
      },
      validator=validator(EditOrderResult),
      validate=validate,
    )

  async def cancel_order(
    self,
    *,
    order_id: str | None = None,
    cli_ord_id: str | None = None,
    validate: bool | None = None,
  ) -> CancelOrderResult:
    """Cancel one order, by ID or client ID."""
    return await self.client.signed(
      'POST',
      f'{API}/cancelorder',
      {'order_id': order_id, 'cliOrdId': cli_ord_id},
      validator=validator(CancelOrderResult),
      validate=validate,
    )

  async def cancel_all_orders(
    self, symbol: str | None = None, *, validate: bool | None = None
  ) -> CancelAllResult:
    """Cancel every open order, or only those of `symbol`."""
    return await self.client.signed(
      'POST',
      f'{API}/cancelallorders',
      {'symbol': symbol},
      validator=validator(CancelAllResult),
      validate=validate,
    )

  async def batch_order(
    self, instructions: Sequence[BatchInstruction], *, validate: bool | None = None
  ) -> BatchOrderResult:
    """Send, edit and cancel orders in one request; one status per instruction."""
    return await self.client.signed(
      'POST',
      f'{API}/batchorder',
      body={'batchOrder': list(instructions)},
      validator=validator(BatchOrderResult),
      validate=validate,
    )

  async def fills(
    self, last_fill_time: datetime | None = None, *, validate: bool | None = None
  ) -> FillsResult:
    """The last 100 own fills, up to `last_fill_time` when given; newest first."""
    return await self.client.signed(
      'GET',
      f'{API}/fills',
      {'lastFillTime': iso(last_fill_time) if last_fill_time is not None else None},
      validator=validator(FillsResult),
      validate=validate,
    )

  async def leverage_preferences(
    self, *, validate: bool | None = None
  ) -> LeveragePreferencesResult:
    """The markets set to isolated margin and their leverage; others trade cross."""
    return await self.client.signed(
      'GET',
      f'{API}/leveragepreferences',
      validator=validator(LeveragePreferencesResult),
      validate=validate,
    )

  async def fee_schedules(self, *, validate: bool | None = None) -> FeeSchedulesResult:
    """Every fee schedule and its volume tiers (public)."""
    return await self.client.request(
      f'{API}/feeschedules',
      validator=validator(FeeSchedulesResult),
      validate=validate,
    )

  async def fee_volumes(self, *, validate: bool | None = None) -> FeeVolumesResult:
    """The account's 30-day USD volume per fee schedule."""
    return await self.client.signed(
      'GET',
      f'{API}/feeschedules/volumes',
      validator=validator(FeeVolumesResult),
      validate=validate,
    )

  async def account_log(
    self,
    *,
    since: datetime | None = None,
    before: datetime | None = None,
    count: int | None = None,
    info: str | None = None,
    validate: bool | None = None,
  ) -> AccountLogResult:
    """Account log rows (funding, fees, transfers, ...) within bounds, newest first.

    Args:
      since: Earliest time, inclusive.
      before: Latest time, exclusive.
      count: Most rows to return.
      info: Only rows of this kind, e.g. `funding rate change`.
    """
    return await self.client.signed(
      'GET',
      f'{HISTORY}/account-log',
      {
        'since': int(since.timestamp() * 1000) if since is not None else None,
        'before': int(before.timestamp() * 1000) if before is not None else None,
        'count': count,
        'info': info,
      },
      validator=validator(AccountLogResult),
      validate=validate,
    )
