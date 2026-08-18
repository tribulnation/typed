from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmUmCurrentPositionMode(TypedDict):
  """Get user's position mode (Hedge Mode or One-way Mode ) on EVERY symbol in UM."""

  dualSidePosition: NotRequired[bool]
  """\"true": Hedge Mode; "false": One-way Mode."""


class UmPositionMode(RpcEndpoint):
  """Get UM Current Position Mode"""

  async def um_position_mode(
    self,
    *,
    validate: bool | None = None,
  ) -> PmUmCurrentPositionMode:
    """Get user's position mode (Hedge Mode or One-way Mode ) on EVERY symbol in UM.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin/api/rest-api/account#get-um-current-position-mode)
    """
    _Response = PmUmCurrentPositionMode
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/papi/v1/um/positionSide/dual', validator=_validator, validate=validate
    )
