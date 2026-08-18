from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class DeletePortfolioResponse(TypedDict):
  """Empty response body confirming deletion."""


@dataclass(frozen=True, kw_only=True)
class Delete(RpcEndpoint):
  """`DELETE /api/v3/brokerage/portfolios/{portfolio_uuid}`."""

  async def delete(self, portfolio_uuid: str) -> DeletePortfolioResponse:
    """Delete a portfolio.

    Args:
      portfolio_uuid: The id of the portfolio to delete.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/portfolios/delete-portfolio)
    """
    return await self.authed_request(
      'DELETE',
      f'/api/v3/brokerage/portfolios/{portfolio_uuid}',
      validator=validator(DeletePortfolioResponse),
    )
