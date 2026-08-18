"""Proposals -- Query all governance proposals, optionally filtered by status, voter, or depositor address."""

from typed_core import PaginatedResponse
from dydx.chain.core import GrpcEndpoint, wrap_exceptions
import dydx.protos.cosmos.gov.v1 as v1_proto
from dydx.protos.cosmos.base.query.v1beta1 import PageRequest
from dydx.protos.cosmos.gov.v1 import Proposal
from dydx.protos.cosmos.gov.v1 import ProposalStatus


class Proposals(GrpcEndpoint):
  """Query all governance proposals, optionally filtered by status, voter, or depositor address."""

  @wrap_exceptions
  async def proposals(
    self,
    proposal_status: ProposalStatus,
    *,
    voter: str,
    depositor: str,
    pagination: PageRequest | None = None,
  ) -> v1_proto.QueryProposalsResponse:
    """Query all governance proposals, optionally filtered by status, voter, or depositor address."""
    return await v1_proto.QueryStub(self.channel).proposals(
      v1_proto.QueryProposalsRequest(
        proposal_status=proposal_status,
        voter=voter,
        depositor=depositor,
        pagination=pagination,
      )
    )

  def proposals_paged(
    self,
    proposal_status: ProposalStatus,
    *,
    voter: str,
    depositor: str,
    limit: int | None = None,
  ) -> PaginatedResponse[Proposal, bytes]:
    """Page through `proposals`, awaitable (flattens every page) or async-iterable
    (one page at a time).
    """

    async def next(key: bytes) -> tuple[list[Proposal], bytes | None]:
      response = await self.proposals(
        proposal_status,
        voter=voter,
        depositor=depositor,
        pagination=PageRequest(key=key, limit=(limit if limit is not None else 0)),
      )
      rows = response.proposals
      state_0 = response.pagination
      state = getattr(state_0, 'next_key', None) if state_0 is not None else None
      return rows, state or None

    return PaginatedResponse(b'', next)
