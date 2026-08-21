"""Cosmos bank spendable balances query."""

from typed_core import PaginatedResponse

from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
from typed_dydx.chain.pagination import next_key, page_request
from typed_dydx.protos.cosmos.bank import v1beta1 as bank_proto
from typed_dydx.protos.cosmos.base import v1beta1 as coin_proto
from typed_dydx.protos.cosmos.base.query import v1beta1 as query_proto

class SpendableBalances(GrpcEndpoint):
  """Bank spendable balances endpoint."""

  @wrap_exceptions
  async def spendable_balances(
    self, address: str, *, pagination: query_proto.PageRequest | None = None,
  ) -> bank_proto.QuerySpendableBalancesResponse:
    """Query spendable balances for an account address."""
    request = bank_proto.QuerySpendableBalancesRequest(address=address, pagination=pagination)
    return await bank_proto.QueryStub(self.channel).spendable_balances(request)

  def spendable_balances_paged(
    self, address: str, *, limit: int | None = None,
  ) -> PaginatedResponse[coin_proto.Coin, bytes]:
    """Page through spendable balances for an account address.

    Args:
      address: Account address to query.
      limit: Optional maximum number of balances per page.

    Returns:
      A paginated response yielding spendable balance pages.
    """
    async def next(key: bytes) -> tuple[list[coin_proto.Coin], bytes | None]:
      """Fetch the next spendable balance page."""
      response = await self.spendable_balances(
        address,
        pagination=page_request(key, limit=limit),
      )
      return response.balances, next_key(response)

    return PaginatedResponse(b'', next)
