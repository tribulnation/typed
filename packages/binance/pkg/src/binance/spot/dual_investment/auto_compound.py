from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class DualInvestmentAutoCompoundStatus(TypedDict):
  """A Dual Investment position's Auto-Compound plan after an update."""

  positionId: NotRequired[str]
  """Position identifier."""
  autoCompoundPlan: NotRequired[str]
  """Auto-compound plan after the update."""


class AutoCompound(RpcEndpoint):
  """Change the Auto-Compound plan on an existing Dual Investment position. Disabled 15:31-16:00 UTC+8 daily."""

  async def auto_compound(
    self,
    *,
    position_id: str,
    auto_compound_plan: Literal['NONE', 'STANDARD', 'ADVANCED'],
    validate: bool | None = None,
  ) -> DualInvestmentAutoCompoundStatus:
    """Change the Auto-Compound plan on an existing Dual Investment position. Disabled 15:31-16:00 UTC+8 daily.

    Args:
      position_id: Position identifier, from spot.dual_investment.positions.
      auto_compound_plan: Auto-compound plan to apply.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-dual-investment/api/rest-api/trade#change-auto-compound-status)
    """
    params: dict = {
      'positionId': position_id,
      'autoCompoundPlan': auto_compound_plan,
    }
    _Response = DualInvestmentAutoCompoundStatus
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/sapi/v1/dci/product/auto_compound/edit-status',
      params=params,
      validator=_validator,
      validate=validate,
    )
