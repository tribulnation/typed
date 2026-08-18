from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class Amount(TypedDict):
  """The amount to move to the target portfolio."""

  value: str
  """The amount of the specified currency."""
  currency: str
  """Currency symbol, e.g. `USD`."""


class MovePortfolioFundsResponse(TypedDict):
  source_portfolio_uuid: NotRequired[str]
  """Id of the portfolio funds were moved from."""
  target_portfolio_uuid: NotRequired[str]
  """Id of the portfolio funds were moved to."""


class MovePortfolioFundsRequest(TypedDict):
  funds: Amount
  source_portfolio_uuid: str
  """Id of the portfolio to move funds from."""
  target_portfolio_uuid: str
  """Id of the portfolio to move funds to."""


@dataclass(frozen=True, kw_only=True)
class MoveFunds(RpcEndpoint):
  """`POST /api/v3/brokerage/portfolios/move_funds`."""

  async def move_funds(
    self,
    move_portfolio_funds_request: MovePortfolioFundsRequest,
  ) -> MovePortfolioFundsResponse:
    """Move funds between two of the calling user's portfolios.

    Args:
      move_portfolio_funds_request: The transfer to make.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/portfolios/move-portfolios-funds)
    """
    return await self.authed_request(
      'POST',
      '/api/v3/brokerage/portfolios/move_funds',
      json=move_portfolio_funds_request,
      validator=validator(MovePortfolioFundsResponse),
    )
