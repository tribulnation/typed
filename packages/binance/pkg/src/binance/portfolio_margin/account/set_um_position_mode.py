from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmChangeUmPositionMode(TypedDict):
  """Change user's position mode (Hedge Mode or One-way Mode ) on EVERY symbol in UM."""

  code: NotRequired[int]
  """Code."""
  msg: NotRequired[str]
  """Msg."""


class SetUmPositionMode(RpcEndpoint):
  """Change UM Position Mode"""

  async def set_um_position_mode(
    self,
    *,
    dual_side_position: Literal['true', 'false'],
    validate: bool | None = None,
  ) -> PmChangeUmPositionMode:
    """Change user's position mode (Hedge Mode or One-way Mode ) on EVERY symbol in UM.

    Args:
      dual_side_position: \"true": Hedge Mode; "false": One-way Mode.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#change-um-position-mode)
    """
    params: dict = {
      'dualSidePosition': dual_side_position,
    }
    _Response = PmChangeUmPositionMode
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'POST',
      '/papi/v1/um/positionSide/dual',
      params=params,
      validator=_validator,
      validate=validate,
    )
