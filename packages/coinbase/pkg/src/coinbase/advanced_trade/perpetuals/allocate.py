from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class AllocatePortfolioRequest(TypedDict):
  """Request to allocate collateral to an isolated position."""

  portfolio_uuid: str
  """The portfolio UUID."""
  symbol: str
  """The trading pair, e.g. "BTC-PERP-INTX"."""
  amount: str
  """The allocation amount for the isolated position."""
  currency: str
  """The currency of the allocation amount, e.g. "USD" or "BTC"."""


class AllocatePortfolioResponse(TypedDict):
  """Empty response confirming the allocation was made."""


@dataclass(frozen=True, kw_only=True)
class Allocate(RpcEndpoint):
  """`POST /api/v3/brokerage/intx/allocate`."""

  async def __call__(
    self,
    allocate_portfolio_request: AllocatePortfolioRequest,
  ) -> AllocatePortfolioResponse:
    """Allocate collateral to an isolated perpetuals position on Coinbase International Exchange (INTX). Deprecated: this INTX perpetuals surface retires 2026-09-09, replaced by a Deribit-powered derivatives gateway (see `upstream.md`).

    Args:
      allocate_portfolio_request: The allocation to make.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/perpetuals/allocate-portfolio)
    """
    return await self.authed_request(
      'POST',
      '/api/v3/brokerage/intx/allocate',
      json=allocate_portfolio_request,
      validator=validator(AllocatePortfolioResponse),
    )
