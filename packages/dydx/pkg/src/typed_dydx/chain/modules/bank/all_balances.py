"""AllBalances -- Query all balances for an account address."""

from typed_core import PaginatedResponse
from typed_dydx.chain.core import GrpcEndpoint, wrap_exceptions
import typed_dydx.protos.cosmos.bank.v1beta1 as v1beta1_proto
from typed_dydx.protos.cosmos.base.query.v1beta1 import PageRequest
from typed_dydx.protos.cosmos.base.v1beta1 import Coin


class AllBalances(GrpcEndpoint):
  """Query all balances for an account address."""

  @wrap_exceptions
  async def all_balances(
    self,
    address: str,
    *,
    pagination: PageRequest | None = None,
    resolve_denom: bool,
  ) -> v1beta1_proto.QueryAllBalancesResponse:
    """Query all balances for an account address."""
    return await v1beta1_proto.QueryStub(self.channel).all_balances(
      v1beta1_proto.QueryAllBalancesRequest(
        address=address, pagination=pagination, resolve_denom=resolve_denom
      )
    )

  def all_balances_paged(
    self,
    address: str,
    *,
    limit: int | None = None,
    resolve_denom: bool,
  ) -> PaginatedResponse[Coin, bytes]:
    """Page through `all_balances`, awaitable (flattens every page) or async-iterable
    (one page at a time).
    """

    async def next(key: bytes) -> tuple[list[Coin], bytes | None]:
      response = await self.all_balances(
        address,
        resolve_denom=resolve_denom,
        pagination=PageRequest(key=key, limit=(limit if limit is not None else 0)),
      )
      rows = response.balances
      state_0 = response.pagination
      state = getattr(state_0, 'next_key', None) if state_0 is not None else None
      return rows, state or None

    return PaginatedResponse(b'', next)
