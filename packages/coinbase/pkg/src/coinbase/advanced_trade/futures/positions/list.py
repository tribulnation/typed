from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Literal, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class FuturesPosition(TypedDict):
  """One open futures position."""

  product_id: str
  """The ticker symbol, e.g. "BIT-28JUL23-CDE"."""
  expiration_time: str
  """The expiry of the position, RFC 3339."""
  side: Literal['UNKNOWN', 'LONG', 'SHORT']
  """The side of the position."""
  number_of_contracts: str
  """The size of the position, in contracts."""
  current_price: str
  """The current price of the product."""
  avg_entry_price: str
  """The average entry price for the current position."""
  unrealized_pnl: str
  """Unrealized profit and loss for the position."""
  daily_realized_pnl: str
  """Realized profit and loss from trades on the current trade date."""


class GetFuturesPositionsResponse(TypedDict):
  """Open futures positions."""

  positions: list[FuturesPosition]
  """One entry per open futures position."""


@dataclass(frozen=True, kw_only=True)
class List(RpcEndpoint):
  """`GET /api/v3/brokerage/cfm/positions`."""

  async def list(self) -> GetFuturesPositionsResponse:
    """List all open positions in the CFM futures wallet.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/futures/list-futures-positions)
    """
    return await self.authed_request(
      'GET',
      '/api/v3/brokerage/cfm/positions',
      validator=validator(GetFuturesPositionsResponse),
    )
