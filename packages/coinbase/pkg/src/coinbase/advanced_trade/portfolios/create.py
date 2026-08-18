from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class CreatePortfolioRequest(TypedDict):
  name: str
  """The name of the portfolio."""


class Portfolio(TypedDict):
  """The created portfolio."""

  name: str
  """Portfolio display name."""
  uuid: str
  """Portfolio id."""
  type: Literal['UNDEFINED', 'DEFAULT', 'CONSUMER', 'INTX']
  """Portfolio classification."""
  deleted: bool
  """Whether the portfolio has been deleted."""


class CreatePortfolioResponse(TypedDict):
  portfolio: NotRequired[Portfolio]


@dataclass(frozen=True, kw_only=True)
class Create(RpcEndpoint):
  """`POST /api/v3/brokerage/portfolios`."""

  async def create(
    self,
    create_portfolio_request: CreatePortfolioRequest,
  ) -> CreatePortfolioResponse:
    """Create a new portfolio.

    Args:
      create_portfolio_request: The portfolio to create.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/portfolios/create-portfolio)
    """
    return await self.authed_request(
      'POST',
      '/api/v3/brokerage/portfolios',
      json=create_portfolio_request,
      validator=validator(CreatePortfolioResponse),
    )
