from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Literal, NotRequired, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class SweepAmount(TypedDict):
  """The requested sweep amount."""

  value: str
  """The amount, as a decimal string."""
  currency: str
  """The currency the amount is denominated in."""
  cbrn: NotRequired[str]
  """CBRN-format token identifier for the currency."""


class FuturesSweep(TypedDict):
  """One sweep request from the futures wallet to the spot wallet."""

  id: str
  """The ID of the scheduled sweep request."""
  requested_amount: SweepAmount
  should_sweep_all: bool
  """Whether the request was to sweep all available funds."""
  status: Literal['PENDING', 'PROCESSING', 'UNKNOWN_FCM_SWEEP_STATUS']
  """Pending sweeps have not started processing and can be cancelled; processing sweeps cannot."""
  scheduled_time: str
  """When the sweep request was submitted, RFC 3339."""


class GetFuturesSweepsResponse(TypedDict):
  """Futures sweep requests."""

  sweeps: list[FuturesSweep]
  """One entry per scheduled sweep."""


@dataclass(frozen=True, kw_only=True)
class List(RpcEndpoint):
  """`GET /api/v3/brokerage/cfm/sweeps`."""

  async def list(self) -> GetFuturesSweepsResponse:
    """List pending and processing sweep requests moving funds from the CFM futures wallet to the USD spot wallet.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/futures/list-futures-sweeps)
    """
    return await self.authed_request(
      'GET',
      '/api/v3/brokerage/cfm/sweeps',
      validator=validator(GetFuturesSweepsResponse),
    )
