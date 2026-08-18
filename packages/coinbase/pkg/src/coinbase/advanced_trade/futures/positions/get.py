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


class GetFuturesPositionResponse(TypedDict):
  """A single futures position."""

  position: FuturesPosition


@dataclass(frozen=True, kw_only=True)
class Get(RpcEndpoint):
  """`GET /api/v3/brokerage/cfm/positions/{product_id}`."""

  async def get(self, product_id: str) -> GetFuturesPositionResponse:
    """Get the open position for a specific futures product in the CFM futures wallet.

    Args:
      product_id: The ticker symbol, e.g. "BIT-28JUL23-CDE".

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/futures/get-futures-position)
    """
    return await self.authed_request(
      'GET',
      f'/api/v3/brokerage/cfm/positions/{product_id}',
      validator=validator(GetFuturesPositionResponse),
    )
