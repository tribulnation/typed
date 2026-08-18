"""`POST /api/v2/getCrossModeMarginRequirement` — Get Cross Margin Requirement."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class CrossMarginRequirement(TypedDict):
  """Cross margin requirement for a hypothetical position on one symbol."""

  symbol: str
  """Symbol of the contract."""
  imr: str
  """Initial margin requirement ratio."""
  mmr: str
  """Maintenance margin requirement ratio."""
  positionValue: str
  """The requested notional position value, echoed back."""
  price: str
  """Reference price used to compute the requirement."""
  size: int
  """Position size, in contracts, implied by `positionValue` at `price`."""


class GetCrossMarginRequirementParams(TypedDict):
  """Symbol, hypothetical position value and leverage to calculate the margin requirement for."""

  symbol: str
  """Symbol of the contract, e.g. `XBTUSDTM`."""
  positionValue: str
  """Hypothetical notional position value, in the contract's quote currency."""
  leverage: str
  """Leverage multiplier to calculate the margin requirement at."""


_Type = list[CrossMarginRequirement]
adapter = validator[_Type](_Type)  # type: ignore


class GetCrossMarginRequirement(RpcEndpoint):
  """`Get Cross Margin Requirement` — mixed into `Positions`, the product exposing `futures.positions.get_cross_margin_requirement`."""

  async def get_cross_margin_requirement(
    self,
    get_cross_margin_requirement_params: GetCrossMarginRequirementParams,
    *,
    validate: bool | None = None,
  ) -> list[CrossMarginRequirement]:
    """Calculate the cross margin requirement (initial and maintenance margin ratios) for a hypothetical position on a symbol, given a notional position value and leverage. A pure calculator -- despite being reachable only by `POST`, it computes a figure rather than mutating any account state.

    Args:
      get_cross_margin_requirement_params: Symbol, hypothetical position value and leverage to calculate the margin requirement for.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v2/getCrossModeMarginRequirement',
      json=get_cross_margin_requirement_params,
      validator=adapter,
      validate=validate,
    )
