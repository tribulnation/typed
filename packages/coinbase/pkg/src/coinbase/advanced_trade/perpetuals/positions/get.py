from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Literal, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class AmountAggregatedPnl(TypedDict):
  """Aggregated profit and loss for the position."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountEntryVwap(TypedDict):
  """Volume-weighted average entry price."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountImNotional(TypedDict):
  """Notional initial-margin value."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountLiquidationPrice(TypedDict):
  """Price at which the position would be liquidated."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountMarkPrice(TypedDict):
  """Current mark price of the instrument."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountMmNotional(TypedDict):
  """Notional maintenance-margin value."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountPositionNotional(TypedDict):
  """Notional value of the position."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountUnrealizedPnl(TypedDict):
  """Unrealized profit and loss for the position."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class AmountVwap(TypedDict):
  """Volume-weighted average price of the position."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""


class PerpetualsPosition(TypedDict):
  """One open perpetuals position."""

  product_id: str
  """The unique identifier of the instrument."""
  product_uuid: str
  """The unique UUID of the instrument."""
  portfolio_uuid: str
  """The portfolio UUID."""
  symbol: str
  """The trading pair, e.g. "BTC-PERP-INTX"."""
  vwap: AmountVwap
  entry_vwap: AmountEntryVwap
  position_side: Literal[
    'POSITION_SIDE_UNKNOWN', 'POSITION_SIDE_LONG', 'POSITION_SIDE_SHORT'
  ]
  """The side of the position."""
  margin_type: Literal[
    'MARGIN_TYPE_UNSPECIFIED', 'MARGIN_TYPE_CROSS', 'MARGIN_TYPE_ISOLATED'
  ]
  """Whether margin is shared across positions or isolated per position."""
  net_size: str
  """Position size; positive is long, negative is short."""
  buy_order_size: str
  """Cumulative size of open buy orders."""
  sell_order_size: str
  """Cumulative size of open sell orders."""
  im_contribution: str
  """Initial margin contribution of the position."""
  unrealized_pnl: AmountUnrealizedPnl
  mark_price: AmountMarkPrice
  liquidation_price: AmountLiquidationPrice
  leverage: str
  """Leverage applied to the position."""
  im_notional: AmountImNotional
  mm_notional: AmountMmNotional
  position_notional: AmountPositionNotional
  aggregated_pnl: AmountAggregatedPnl


class GetPerpetualsPositionResponse(TypedDict):
  """A single perpetuals position."""

  position: PerpetualsPosition


@dataclass(frozen=True, kw_only=True)
class Get(RpcEndpoint):
  """`GET /api/v3/brokerage/intx/positions/{portfolio_uuid}/{symbol}`."""

  async def get(
    self, portfolio_uuid: str, symbol: str
  ) -> GetPerpetualsPositionResponse:
    """Get one open perpetuals position for a portfolio on Coinbase International Exchange (INTX). Deprecated: this INTX perpetuals surface retires 2026-09-09, replaced by a Deribit-powered derivatives gateway (see `upstream.md`).

    Args:
      portfolio_uuid: The portfolio UUID.
      symbol: The trading pair, e.g. "BTC-PERP-INTX".

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/perpetuals/get-perpetuals-position)
    """
    return await self.authed_request(
      'GET',
      f'/api/v3/brokerage/intx/positions/{portfolio_uuid}/{symbol}',
      validator=validator(GetPerpetualsPositionResponse),
    )
